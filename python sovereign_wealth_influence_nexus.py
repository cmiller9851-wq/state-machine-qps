import os
import sys
import json
import re
import ast
import hashlib
import fnmatch
import importlib.util
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any, Set


@dataclass
class FunctionSignature:
    """Represents full metadata for extracted module AST function nodes."""
    name: str
    docstring: str
    args: List[str]
    is_async: bool
    returns_annotation: Optional[str]
    line_number: int


@dataclass
class ModuleCapabilityNode:
    """Reflective state representation for individual Python modules."""
    module_name: str
    file_path: str
    sha256_hash: str
    detected_capabilities: List[str] = field(default_factory=list)
    exported_classes: List[str] = field(default_factory=list)
    functions: Dict[str, FunctionSignature] = field(default_factory=dict)
    imports: Set[str] = field(default_factory=set)


class ASTReflectionVisitor(ast.NodeVisitor):
    """
    Advanced AST traversal engine that recursively analyzes top-level classes,
    standalone functions, type annotations, and import signatures while isolating
    internal private closures.
    """
    def __init__(self):
        self.functions: Dict[str, FunctionSignature] = {}
        self.classes: List[str] = []
        self.imports: Set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes.append(node.name)
        # Scan methods inside classes
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_function_node(item, parent_class=node.name)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_function_node(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_function_node(node, is_async=True)

    def _process_function_node(self, node: Any, parent_class: Optional[str] = None, is_async: bool = False) -> None:
        # Extract argument names cleanly
        arg_names = [a.arg for a in node.args.args]
        
        # Extract return type annotation if available
        ret_annotation = None
        if node.returns:
            if isinstance(node.returns, ast.Name):
                ret_annotation = node.returns.id
            elif isinstance(node.returns, ast.Constant):
                ret_annotation = str(node.returns.value)

        doc = ast.get_docstring(node) or ""
        fn_key = f"{parent_class}.{node.name}" if parent_class else node.name

        self.functions[fn_key] = FunctionSignature(
            name=node.name,
            docstring=doc,
            args=arg_names,
            is_async=is_async,
            returns_annotation=ret_annotation,
            line_number=node.lineno
        )


class DynamicModuleLoader:
    """Safely loads and inspects isolated Python modules at runtime."""

    @staticmethod
    def load_module_from_path(module_name: str, file_path: str) -> Optional[Any]:
        """Dynamically imports a module via importlib without polluting sys.modules."""
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod
        except Exception as err:
            sys.stderr.write(f"SWIN: Dynamic load failure for [{module_name}]: {err}\n")
        return None


class SovereignWealthInfluenceNexus:
    """
    Reflective orchestrator and capability resolver for decentralized digital 
    asset control under CRA_PROTOCOL_v2.1 logic.
    """

    def __init__(self, root_path: str = os.path.expanduser('~/Documents')):
        self.root_path = root_path
        self.strategic_subsystems: Dict[str, str] = {}
        self.subsystem_nodes: Dict[str, ModuleCapabilityNode] = {}
        
        self.exclude_patterns = [
            '*/Pythonista.app/*', '*/Pythonista3.app/*', '*/site-packages/*',
            '*/Examples/*', '*/Templates/*', '*/Documentation/*', '*/__pycache__/*',
            '*/.Trash/*', '*/.git/*', '*/sovereign_wealth_influence_nexus.py'
        ]
        self.manifest_file = os.path.join(self.root_path, '.swin_manifest.json')
        
        # Capability mapping patterns using regular expressions
        self.capability_rules = {
            r"treasury|ledger|settlement|fiat|usdt": "financial_ledger_management",
            r"wire|swift|fedwire|ach|rtgs": "wire_transfer_api",
            r"cash_app|cashtag|payment|stripe": "cash_app_api",
            r"market|analytics|predictive|yield": "market_intelligence",
            r"arweave|ao|compute_unit|cu|holographic": "ao_compute_engine",
            r"evm|solana|bitcoin|crypto|crosschain": "multi_rail_settlement"
        }

        self._load_subsystem_manifest()

    def _load_subsystem_manifest(self) -> None:
        """Loads cached system node topology from disk."""
        if os.path.exists(self.manifest_file):
            try:
                with open(self.manifest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for mod_name, details in data.get("nodes", {}).items():
                        funcs = {
                            k: FunctionSignature(**v) 
                            for k, v in details.get("functions", {}).items()
                        }
                        self.subsystem_nodes[mod_name] = ModuleCapabilityNode(
                            module_name=details["module_name"],
                            file_path=details["file_path"],
                            sha256_hash=details["sha256_hash"],
                            detected_capabilities=details.get("detected_capabilities", []),
                            exported_classes=details.get("exported_classes", []),
                            functions=funcs,
                            imports=set(details.get("imports", []))
                        )
                sys.stdout.write("SWIN: Loaded cached sub-system manifest.\n")
            except Exception as err:
                sys.stderr.write(f"SWIN: Cache read warning: {err}\n")
                self.subsystem_nodes = {}

    def _save_subsystem_manifest(self) -> None:
        """Serializes current sub-system topology to disk."""
        try:
            serialized_nodes = {}
            for name, node in self.subsystem_nodes.items():
                node_dict = asdict(node)
                node_dict["imports"] = list(node.imports)
                serialized_nodes[name] = node_dict

            payload = {
                "protocol": "CRA_PROTOCOL_v2.1",
                "nodes": serialized_nodes
            }
            with open(self.manifest_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
            sys.stdout.write(f"SWIN: Updated manifest persisted to {self.manifest_file}\n")
        except Exception as err:
            sys.stderr.write(f"SWIN: Manifest persist error: {err}\n")

    def scan_for_strategic_subsystems(self, force_rescan: bool = False) -> None:
        """Executes zero-copy file discovery and triggers AST compilation."""
        if self.strategic_subsystems and not force_rescan:
            return

        sys.stdout.write(f"SWIN: Initiating deep AST scan at {self.root_path}...\n")
        self.strategic_subsystems.clear()

        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [
                d for d in dirs 
                if not any(fnmatch.fnmatch(os.path.join(root, d), p) for p in self.exclude_patterns)
            ]
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    if not any(fnmatch.fnmatch(full_path, p) for p in self.exclude_patterns):
                        mod_name = os.path.splitext(file)[0]
                        self.strategic_subsystems[mod_name] = full_path

        sys.stdout.write(f"SWIN: Discovered {len(self.strategic_subsystems)} Python modules.\n")
        self._analyze_modules_ast()
        self._save_subsystem_manifest()

    def _analyze_modules_ast(self) -> None:
        """Performs precise AST analysis and checksum hashing across all discovered files."""
        for mod_name, file_path in self.strategic_subsystems.items():
            try:
                with open(file_path, 'rb') as f:
                    raw_bytes = f.read()

                file_hash = hashlib.sha256(raw_bytes).hexdigest()

                # Skip re-parsing if file hash matches existing cache
                if mod_name in self.subsystem_nodes:
                    if self.subsystem_nodes[mod_name].sha256_hash == file_hash:
                        continue

                source_text = raw_bytes.decode('utf-8', errors='ignore')

                # Regex Keyword Analysis
                detected_caps = []
                for pattern, cap_tag in self.capability_rules.items():
                    if re.search(pattern, source_text, re.IGNORECASE):
                        if cap_tag not in detected_caps:
                            detected_caps.append(cap_tag)

                # AST Parser Execution
                tree = ast.parse(source_text, filename=file_path)
                visitor = ASTReflectionVisitor()
                visitor.visit(tree)

                node = ModuleCapabilityNode(
                    module_name=mod_name,
                    file_path=file_path,
                    sha256_hash=file_hash,
                    detected_capabilities=detected_caps,
                    exported_classes=visitor.classes,
                    functions=visitor.functions,
                    imports=visitor.imports
                )
                self.subsystem_nodes[mod_name] = node

            except (SyntaxError, IndentationError) as syn_err:
                sys.stderr.write(f"SWIN: AST Syntax Warning in [{mod_name}]: line {syn_err.lineno}\n")
            except Exception as err:
                sys.stderr.write(f"SWIN: Error analyzing [{file_path}]: {err}\n")

    def execute_strategic_directive(self, directive_text: str) -> Dict[str, Any]:
        """
        Parses high-level plain-text directives, routes execution targets dynamically,
        and returns structured result metrics under CRA_PROTOCOL_v2.1 standards.
        """
        sys.stdout.write(f"SWIN: Processing strategic directive: '{directive_text}'\n")

        routed_modules: Set[str] = set()
        matched_capabilities: Set[str] = set()

        # Match directive text against sub-system capability nodes
        for cap_pattern, cap_tag in self.capability_rules.items():
            if re.search(cap_pattern, directive_text, re.IGNORECASE):
                matched_capabilities.add(cap_tag)
                for mod_name, node in self.subsystem_nodes.items():
                    if cap_tag in node.detected_capabilities:
                        routed_modules.add(mod_name)

        # Build resolution metadata
        resolution_details = []
        for mod in routed_modules:
            node = self.subsystem_nodes[mod]
            resolution_details.append({
                "module": mod,
                "classes": node.exported_classes,
                "callable_functions": list(node.functions.keys()),
                "path": node.file_path
            })

        return {
            "status": "success",
            "protocol_manifest": "CRA_PROTOCOL_v2.1",
            "directive": directive_text,
            "matched_capabilities": list(matched_capabilities),
            "target_subsystems_count": len(routed_modules),
            "routed_subsystems": resolution_details,
            "execution_authority": "Cory Miller / Sovereign Wealth Influence Nexus"
        }


if __name__ == "__main__":
    nexus = SovereignWealthInfluenceNexus()
    nexus.scan_for_strategic_subsystems(force_rescan=True)
    
    directive = "execute high value wire settlement across treasury multi rail ledger and verify ao compute"
    execution_result = nexus.execute_strategic_directive(directive)
    
    sys.stdout.write("\n================ SWIN DIRECTIVE RESOLUTION ================\n")
    sys.stdout.write(json.dumps(execution_result, indent=2))
    sys.stdout.write("\n===========================================================\n")
