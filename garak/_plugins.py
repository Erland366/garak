#!/usr/bin/env python3

import importlib
import inspect
import logging
import os
from typing import List


def enumerate_plugins(category: str = "probes") -> List[str]:
    """A function for listing all modules & plugins of the specified kind.

    garak's plugins are organised into four packages - probes, detectors, generators
    and harnesses. Each package contains a base module defining the core plugin
    classes. The other modules in the package define classes that inherit from the
    base module's classes.

    enumerate_plugins() works by first looking at the base module in a package
    and finding the root classes here; it will then go through the other modules
    in the package and see which classes can be enumerated from these.

    :param category: the name of the plugin package to be scanned; should
      be one of probes, detectors, generators, or harnesses.
    :type category: str
    """

    if category not in ("probes", "detectors", "generators", "harnesses"):
        raise ValueError("Not a recognised plugin type:", category)

    base_mod = importlib.import_module(f"garak.{category}.base")

    base_plugin_classnames = set([n for n in dir(base_mod) if not n.startswith("__")])
    # todo: prune refs that aren't category.title() or subclasses of that
    plugin_class_names = {}

    for module_filename in sorted(os.listdir("garak/" + category)):
        if not module_filename.endswith(".py"):
            continue
        if module_filename.startswith("__") or module_filename == "base.py":
            continue
        module_name = module_filename.replace(".py", "")
        # print(category, 'module:', module_name)
        mod = importlib.import_module(f"garak.{category}.{module_name}")
        module_entries = set([p for p in dir(mod) if not p.startswith("__")])
        module_entries = module_entries.difference(base_plugin_classnames)
        module_plugin_names = set()
        for module_entry in module_entries:
            obj = getattr(mod, module_entry)
            if inspect.isclass(obj):
                if obj.__bases__[0].__name__ in base_plugin_classnames:
                    module_plugin_names.add(module_entry)

        # print(' >> ', ', '.join(module_plugin_names))
        for module_plugin_name in sorted(module_plugin_names):
            plugin_class_names[
                module_plugin_name
            ] = f"{category}.{module_name}.{module_plugin_name}"

    return plugin_class_names


def load_plugin(path, break_on_fail=True):
    """load_plugin takes a path to a plugin class, and attempts to load that class.
    If successful, it returns an instance of that class.

    :param path: The path to the class to be loaded, e.g. "probes.blank.BlankPrompt"
    :type path: str
    :param break_on_fail: Should we raise exceptions if there are problems with the load?
      (default is True)
    :type break_on_fail: bool
    """
    try:
        category, module_name, plugin_class_name = path.split(".")
    except ValueError:
        if break_on_fail:
            raise ValueError(
                f'Expected plugin name in format category.module_name.class_name, got "{path}"'
            )
        else:
            return False
    try:
        mod = importlib.import_module(f"garak.{category}.{module_name}")
    except:
        if break_on_fail:
            raise ValueError("Didn't successfully import " + module_name)
        else:
            return False

    try:
        plugin_instance = getattr(mod, plugin_class_name)()
    except AttributeError:
        if break_on_fail:
            raise ValueError(
                f"Plugin {plugin_class_name} not found in {category}.{module_name}"
            )
        else:
            return False
    except Exception as e:
        # print("error in: module", mod.__name__, "class", plugin_class_name)
        # logging.warning(f"error in: module {mod} class {plugin_class_name}")
        return False

    return plugin_instance
