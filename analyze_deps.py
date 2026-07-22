import ast,os,json,subprocess,re
root=r'e:\Websites\karate\sk-martial-arts-academy-website-final'
req_file=os.path.join(root,'requirements.txt')

def read_requirements(path):
    reqs=[]
    if not os.path.exists(path):
        return reqs
    with open(path,'r',encoding='utf-8',errors='ignore') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#'):
                continue
            # remove numbering like '1. Django==...'
            line=re.sub(r'^\d+\.\s*','',line)
            reqs.append(line)
    return reqs

reqs = read_requirements(req_file)

# get installed packages
p = subprocess.check_output(['python','-m','pip','list','--format=json'])
installed = json.loads(p.decode('utf-8',errors='ignore'))
installed_map = {pkg['name'].lower():pkg['version'] for pkg in installed}

# get outdated
q = subprocess.check_output(['python','-m','pip','list','--outdated','--format=json'])
outdated = json.loads(q.decode('utf-8',errors='ignore'))
outdated_map = {pkg['name'].lower():pkg for pkg in outdated}

# analyze imports
exclude_dirs={'.venv','venv','env','__pycache__','node_modules','.git','.audit-venv'}
used=set(); py_files=[]
for dirpath,dirnames,filenames in os.walk(root):
    # skip excluded directories in any part of path
    rel = os.path.relpath(dirpath, root)
    parts = set(rel.split(os.sep)) if rel!='.' else set()
    if parts & exclude_dirs:
        continue
    for fn in filenames:
        if fn.endswith('.py'):
            py_files.append(os.path.join(dirpath, fn))

for fp in py_files:
    try:
        with open(fp,'rb') as f:
            src=f.read()
        try:
            tree=ast.parse(src, filename=fp)
        except Exception:
            try:
                tree=ast.parse(src.decode('utf-8','ignore'))
            except Exception:
                continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    used.add(n.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    used.add(node.module.split('.')[0])
    except Exception:
        pass

used_low = set([u.lower() for u in used])
# mapping heuristics
special_map = {'pil':'pillow','pillow':'pillow','pilimage':'pillow','pil':'pillow','dotenv':'python-dotenv','python_dotenv':'python-dotenv','mysqldb':'mysqlclient','mysqlclient':'mysqlclient','django':'django','whitenoise':'whitenoise'}

# try to map used module names to installed package names
mapped_used = set()
for pkg_lower in installed_map.keys():
    # direct match
    if pkg_lower in used_low:
        mapped_used.add(pkg_lower)
        continue
    # used module equals package or vice versa
    for u in used_low:
        if u==pkg_lower or u in pkg_lower or pkg_lower in u:
            mapped_used.add(pkg_lower)
            break
# apply special_map
for u in used_low:
    if u in special_map:
        mapped_used.add(special_map[u])

# combine declared requirements (normalize names without versions)
declared = []
for r in reqs:
    # split off version specifier
    name = re.split('[<>=!~]',r)[0].strip()
    declared.append(name)
declared_low=[d.lower() for d in declared]

# required packages = declared ∪ mapped_used where installed
required = set()
for d in declared_low:
    if d in installed_map:
        required.add(d)
    else:
        # include declared even if not installed locally
        required.add(d)
for m in mapped_used:
    if m in installed_map:
        required.add(m)

# refine: ensure django always included if used
if 'django' in used_low and 'django' in installed_map:
    required.add('django')

# compute unused installed
# Exclude obvious packaging/runtime tools from removal list
never_remove = {'pip','pip-api','pip_audit','setuptools','wheel','pkginfo','platformdirs'}
installed_set=set(installed_map.keys())
unused_installed = sorted(list((installed_set - required) - never_remove))

# suggest can_be_removed as unused_installed but exclude items that are small deps used by tools (heuristic): keep packaging, packaging_legacy maybe
can_be_removed = [p for p in unused_installed if not p.startswith('pip')]

# recommended upgrades: check outdated_map intersection with required
recommend_upgrade = []
for pkg in required:
    if pkg in outdated_map:
        recommend_upgrade.append({'name':outdated_map[pkg]['name'],'current':outdated_map[pkg]['version'],'latest':outdated_map[pkg]['latest_version']})

# build clean requirements: include exact versions from installed for required packages
clean_reqs = []
for pkg in sorted(required):
    ver = installed_map.get(pkg)
    if ver:
        clean_reqs.append(f"{pkg}=={ver}")
    else:
        clean_reqs.append(pkg)

out = {
    'declared_requirements_raw': reqs,
    'declared_requirements': declared,
    'installed_count': len(installed_map),
    'used_module_count': len(used_low),
    'mapped_used_candidates': sorted(list(mapped_used)),
    'required_packages': sorted(list(required)),
    'unused_installed_packages_sample': unused_installed[:200],
    'can_be_removed_sample': can_be_removed[:200],
    'recommended_upgrades': recommend_upgrade,
    'clean_requirements_txt': '\n'.join(clean_reqs)
}
print(json.dumps(out,indent=2))
