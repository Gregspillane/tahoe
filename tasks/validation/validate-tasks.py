#!/usr/bin/env python3
"""Validate all task files for completeness and dependencies."""

import yaml
import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Any


class TaskValidator:
    """Validates task YAML files for Project Tahoe."""
    
    def __init__(self, tasks_dir: Path = Path("tasks")):
        self.tasks_dir = tasks_dir
        self.all_tasks: Dict[str, Dict] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> bool:
        """Validate all task files in the repository."""
        print("🔍 Starting task validation...\n")
        
        # Load all tasks
        if not self._load_all_tasks():
            return False
        
        # Validate individual tasks
        for task_file in self._get_task_files():
            self._validate_task_file(task_file)
        
        # Validate dependencies
        self._validate_dependencies()
        
        # Validate release structure
        self._validate_releases()
        
        # Report results
        return self._report_results()
    
    def _get_task_files(self) -> List[Path]:
        """Get all task YAML files."""
        task_files = []
        for release_dir in self.tasks_dir.glob("r*-*/"):
            if release_dir.is_dir():
                task_files.extend(release_dir.glob("*.yaml"))
        return sorted(task_files)
    
    def _load_all_tasks(self) -> bool:
        """Load all tasks into memory."""
        task_files = self._get_task_files()
        
        if not task_files:
            self.errors.append("No task files found")
            return False
        
        for task_file in task_files:
            try:
                with open(task_file) as f:
                    task_data = yaml.safe_load(f)
                    if task_data and "task" in task_data:
                        task_id = task_data["task"].get("id")
                        if task_id:
                            self.all_tasks[task_id] = task_data
                            print(f"✓ Loaded: {task_id}")
            except Exception as e:
                self.errors.append(f"Failed to load {task_file}: {e}")
                return False
        
        print(f"\n📦 Loaded {len(self.all_tasks)} tasks\n")
        return True
    
    def _validate_task_file(self, filepath: Path) -> bool:
        """Validate a single task file."""
        try:
            with open(filepath) as f:
                task = yaml.safe_load(f)
            
            if not task:
                self.errors.append(f"{filepath}: Empty file")
                return False
            
            # Check required top-level fields
            required_fields = ["task", "context", "implementation", "validation"]
            for field in required_fields:
                if field not in task:
                    self.errors.append(f"{filepath}: Missing required field '{field}'")
                    return False
            
            # Validate task section
            task_section = task.get("task", {})
            task_id = task_section.get("id", "unknown")
            
            required_task_fields = ["id", "name", "description", "complexity", "estimated_hours"]
            for field in required_task_fields:
                if field not in task_section:
                    self.errors.append(f"{task_id}: Missing task.{field}")
            
            # Validate complexity
            if task_section.get("complexity") not in ["simple", "medium", "complex"]:
                self.errors.append(f"{task_id}: Invalid complexity value")
            
            # Validate context section
            context = task.get("context", {})
            required_context_fields = ["why", "architectural_role", "depends_on_tasks", "enables_tasks"]
            for field in required_context_fields:
                if field not in context:
                    self.errors.append(f"{task_id}: Missing context.{field}")
            
            # Validate ADK components
            adk = task.get("adk_components", {})
            if not adk.get("imports_needed"):
                self.warnings.append(f"{task_id}: No ADK imports specified")
            
            # Validate implementation section
            impl = task.get("implementation", {})
            if not impl.get("creates") and not impl.get("modifies"):
                self.errors.append(f"{task_id}: Must create or modify at least one file")
            
            # Validate implementation steps
            steps = impl.get("implementation_steps", [])
            if len(steps) < 2:
                self.warnings.append(f"{task_id}: Should have at least 2 implementation steps")
            
            for i, step in enumerate(steps):
                if "step" not in step:
                    self.errors.append(f"{task_id}: Step {i+1} missing 'step' description")
                if "focus" not in step:
                    self.warnings.append(f"{task_id}: Step {i+1} missing 'focus' points")
            
            # Validate validation section
            validation = task.get("validation", {})
            commands = validation.get("commands", [])
            if len(commands) < 3:
                self.warnings.append(f"{task_id}: Should have at least 3 validation commands")
            
            for i, cmd in enumerate(commands):
                if "desc" not in cmd:
                    self.errors.append(f"{task_id}: Validation command {i+1} missing description")
                if "run" not in cmd:
                    self.errors.append(f"{task_id}: Validation command {i+1} missing run command")
                if "expects" not in cmd:
                    self.warnings.append(f"{task_id}: Validation command {i+1} missing expected output")
            
            # Validate success criteria
            if not task.get("success_criteria"):
                self.warnings.append(f"{task_id}: Missing success criteria")
            elif len(task.get("success_criteria", [])) < 3:
                self.warnings.append(f"{task_id}: Should have at least 3 success criteria")
            
            # Validate session notes
            notes = task.get("session_notes", {})
            if not notes.get("decisions_made"):
                self.warnings.append(f"{task_id}: Missing session_notes.decisions_made")
            if not notes.get("patterns_established"):
                self.warnings.append(f"{task_id}: Missing session_notes.patterns_established")
            if not notes.get("context_for_next"):
                self.warnings.append(f"{task_id}: Missing session_notes.context_for_next")
            
            print(f"✓ Validated: {task_id}")
            return True
            
        except yaml.YAMLError as e:
            self.errors.append(f"{filepath}: Invalid YAML - {e}")
            return False
        except Exception as e:
            self.errors.append(f"{filepath}: Validation error - {e}")
            return False
    
    def _validate_dependencies(self):
        """Validate task dependencies exist."""
        print("\n🔗 Validating dependencies...")
        
        all_task_ids = set(self.all_tasks.keys())
        
        for task_id, task_data in self.all_tasks.items():
            context = task_data.get("context", {})
            
            # Check depends_on_tasks
            depends_on = context.get("depends_on_tasks", [])
            for dep in depends_on:
                if dep and dep not in all_task_ids:
                    self.errors.append(f"{task_id}: Dependency '{dep}' does not exist")
            
            # Check enables_tasks
            enables = context.get("enables_tasks", [])
            for enabled in enables:
                if enabled and enabled not in all_task_ids:
                    self.warnings.append(f"{task_id}: Enabled task '{enabled}' does not exist")
            
            # Check uses_from_previous
            impl = task_data.get("implementation", {})
            uses = impl.get("uses_from_previous", [])
            for use in uses:
                from_task = use.get("from_task")
                if from_task and from_task not in all_task_ids:
                    self.errors.append(f"{task_id}: Referenced task '{from_task}' does not exist")
        
        print("✓ Dependencies validated")
    
    def _validate_releases(self):
        """Validate release structure and tasks."""
        print("\n📋 Validating releases...")
        
        releases_file = self.tasks_dir / "releases.yaml"
        if not releases_file.exists():
            self.errors.append("releases.yaml not found")
            return
        
        try:
            with open(releases_file) as f:
                releases_data = yaml.safe_load(f)
            
            if not releases_data or "releases" not in releases_data:
                self.errors.append("releases.yaml: Missing 'releases' section")
                return
            
            releases = releases_data.get("releases", [])
            release_ids = set()
            
            for release in releases:
                release_id = release.get("id")
                if not release_id:
                    self.errors.append("Release missing 'id'")
                    continue
                
                if release_id in release_ids:
                    self.errors.append(f"Duplicate release ID: {release_id}")
                release_ids.add(release_id)
                
                # Check required fields
                required_fields = ["name", "description", "tasks"]
                for field in required_fields:
                    if field not in release:
                        self.errors.append(f"{release_id}: Missing field '{field}'")
                
                # Validate task references
                tasks = release.get("tasks", [])
                for task_ref in tasks:
                    # Convert task reference to full ID (e.g., r1-t01 -> r1-t01-*)
                    matching_tasks = [tid for tid in self.all_tasks.keys() if tid.startswith(task_ref)]
                    if not matching_tasks:
                        self.errors.append(f"{release_id}: Task '{task_ref}' not found")
                
                # Check dependencies
                requires = release.get("requires", [])
                for req in requires:
                    if req not in release_ids and req != release_id:
                        self.warnings.append(f"{release_id}: Required release '{req}' not found")
            
            print(f"✓ Validated {len(releases)} releases")
            
        except Exception as e:
            self.errors.append(f"releases.yaml: {e}")
    
    def _report_results(self) -> bool:
        """Report validation results."""
        print("\n" + "="*60)
        print("VALIDATION REPORT")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All tasks valid - no issues found!")
        elif not self.errors:
            print(f"\n✅ Validation passed with {len(self.warnings)} warnings")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} errors")
        
        print("\n" + "="*60)
        
        # Summary statistics
        print("\n📊 STATISTICS:")
        print(f"  • Total tasks: {len(self.all_tasks)}")
        print(f"  • Releases: {len([d for d in self.tasks_dir.iterdir() if d.is_dir() and d.name.startswith('r')])}")
        print(f"  • Errors: {len(self.errors)}")
        print(f"  • Warnings: {len(self.warnings)}")
        
        return len(self.errors) == 0
    
    def generate_dependency_graph(self):
        """Generate a dependency graph in Mermaid format."""
        print("\n📈 Generating dependency graph...")
        
        graph = ["graph TD"]
        
        for task_id, task_data in sorted(self.all_tasks.items()):
            context = task_data.get("context", {})
            task_name = task_data.get("task", {}).get("name", task_id)
            
            # Add node
            graph.append(f'    {task_id}["{task_id}<br/>{task_name}"]')
            
            # Add dependencies
            depends_on = context.get("depends_on_tasks", [])
            for dep in depends_on:
                if dep:
                    graph.append(f"    {dep} --> {task_id}")
        
        # Save to file
        graph_file = self.tasks_dir / "task-dependencies.mmd"
        with open(graph_file, "w") as f:
            f.write("\n".join(graph))
        
        print(f"✓ Dependency graph saved to {graph_file}")


def main():
    """Main entry point."""
    validator = TaskValidator()
    
    # Run validation
    success = validator.validate_all()
    
    # Generate dependency graph
    validator.generate_dependency_graph()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()