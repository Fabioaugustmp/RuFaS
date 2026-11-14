import ast, sys, os, re
from collections import defaultdict, deque
ROOT = sys.argv[1]
funcs = {}          # qualname -> (file, lineno)
calls = defaultdict(set)  # qualname -> set(callee simple names)
name_index = defaultdict(set)  # simple name -> qualnames

for dp, _, fns in os.walk(os.path.join(ROOT, "RUFAS")):
    for fn in fns:
        if not fn.endswith(".py"): continue
        path = os.path.join(dp, fn)
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        try:
            tree = ast.parse(open(path, encoding="utf-8").read())
        except Exception:
            continue
        mod = rel[:-3].replace("/", ".")
        def visit(node, prefix):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    q = f"{mod}:{prefix}{child.name}"
                    funcs[q] = (rel, child.lineno)
                    name_index[child.name].add(q)
                    for sub in ast.walk(child):
                        if isinstance(sub, ast.Call):
                            f = sub.func
                            if isinstance(f, ast.Name): calls[q].add(f.id)
                            elif isinstance(f, ast.Attribute): calls[q].add(f.attr)
                    visit(child, prefix + child.name + ".")
                elif isinstance(child, ast.ClassDef):
                    visit(child, prefix + child.name + ".")
                else:
                    visit(child, prefix)
        visit(tree, "")

# Model entry points we care about (simple names of calls that run a model)
MODEL_SINKS = {
 "calculate_requirements": "Exigências NASEM/NRC (DMI e nutrientes)",
 "calculate_heifer_methane": "Metano entérico (novilhas)",
 "calculate_cow_methane": "Metano entérico (vacas)",
 "_calculate_IPCC_methane": "Metano entérico IPCC",
 "calculate_predicted_305_day_milk_yield": "Curva de Wood (previsão 305 dias)",
 "calculate_daily_milk_production": "Curva de Wood (produção diária)",
 "formulate_optimized_ration": "Otimização de ração (scipy.minimize)",
 "attempt_optimization": "Otimização de ração (scipy.minimize)",
 "minimize": "scipy.optimize.minimize (genérico)",
 "truncnorm": "Estocástico (truncnorm)",
}
# Functions that directly contain a sink call
sink_hosts = defaultdict(set)
for q, cs in calls.items():
    for s in cs & set(MODEL_SINKS):
        sink_hosts[s].add(q)

# Reverse graph by simple names -> callers (approximate: name-based)
callers = defaultdict(set)
for q, cs in calls.items():
    for c in cs:
        callers[c].add(q)

ENTRY = "_execute_full_farm_daily_simulation"
entries = {q for q in funcs if q.endswith(":SimulationEngine._execute_full_farm_daily_simulation") or q.endswith("." + ENTRY)}

def path_to_entry(start, maxdepth=12):
    # BFS upward through callers until an entry/daily routine
    seen = {start: None}
    dq = deque([(start, 0)])
    while dq:
        cur, d = dq.popleft()
        simple = cur.split(":")[-1].split(".")[-1]
        if simple.startswith("_execute") or simple in ("_run_simulation_main_loop","simulate","_annual_simulation","_execute_animals_only_daily_simulation","_execute_field_and_feed_daily_simulation"):
            chain = []
            n = cur
            while n is not None:
                chain.append(n); n = seen[n]
            return chain
        if d >= maxdepth: continue
        for cname in callers.get(simple, ()):
            if cname not in seen:
                seen[cname] = cur
                dq.append((cname, d+1))
    return None

print("== Sinks de modelo e funções que os chamam ==")
for s, desc in MODEL_SINKS.items():
    hosts = sorted(sink_hosts.get(s, []))
    if not hosts: continue
    print(f"\n[{s}] {desc}")
    for h in hosts:
        f, ln = funcs[h]
        print(f"   host: {h}  ({f}:{ln})")
        chain = path_to_entry(h)
        if chain:
            print("     caminho até o laço diário:", " <- ".join(c.split(':')[-1] for c in chain[:6]))
