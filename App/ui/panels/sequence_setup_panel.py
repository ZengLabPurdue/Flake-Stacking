import threading
import tkinter as tk
from tkinter import messagebox, ttk


class SequenceSetupPanel:
    COMMANDS = (
        {
            "label": "Stage: Move to XY",
            "device": "stage",
            "operation": "move_to_xy",
            "arguments": ("X (um)", "Y (um)"),
            "types": (int, int),
        },
        {
            "label": "Stage: Step Forward",
            "device": "stage",
            "operation": "step_forward",
            "arguments": (),
            "types": (),
        },
        {
            "label": "Stage: Step Backward",
            "device": "stage",
            "operation": "step_backward",
            "arguments": (),
            "types": (),
        },
        {
            "label": "Stage: Step Left",
            "device": "stage",
            "operation": "step_left",
            "arguments": (),
            "types": (),
        },
        {
            "label": "Stage: Step Right",
            "device": "stage",
            "operation": "step_right",
            "arguments": (),
            "types": (),
        },
        {
            "label": "Thor: Move to XY",
            "device": "thor",
            "operation": "go_to_xypos",
            "arguments": ("X", "Y"),
            "types": (int, int),
        },
        {
            "label": "Thor: Move to Z",
            "device": "thor",
            "operation": "go_to_zpos",
            "arguments": ("Z",),
            "types": (int,),
        },
        {
            "label": "Thor: Rotate to angle",
            "device": "thor",
            "operation": "go_to_angle",
            "arguments": ("Angle",),
            "types": (int,),
        },
        {
            "label": "Thor: Step Forward",
            "device": "thor",
            "operation": "step_forward",
            "arguments": (),
            "types": (),
        },
        {
            "label": "Thor: Step Backward",
            "device": "thor",
            "operation": "step_backward",
            "arguments": (),
            "types": (),
        },
        {
            "label": "Thor: Step Left",
            "device": "thor",
            "operation": "step_left",
            "arguments": (),
            "types": (),
        },
        {
            "label": "Thor: Step Right",
            "device": "thor",
            "operation": "step_right",
            "arguments": (),
            "types": (),
        },
        {
            "label": "Thor: Step Up",
            "device": "thor",
            "operation": "step_up",
            "arguments": (),
            "types": (),
        },
        {
            "label": "Thor: Step Down",
            "device": "thor",
            "operation": "step_down",
            "arguments": (),
            "types": (),
        },
    )

    def __init__(self, parent, root, app):
        self.parent = parent
        self.root = root
        self.app = app
        self.actions = {}
        self._next_action_id = 1
        self._drag_source = None
        self._selected_action_id = None
        self._cancel_event = threading.Event()
        self._is_running = False

        self.frame = self._build_panel()

    def _build_panel(self):
        panel = tk.Frame(self.parent, bg="#f0f0f0", width=404, height=590)
        background = tk.Frame(panel, bg="white", width=400, height=588)
        background.place(x=2, y=0)

        tk.Label(
            background,
            text="Sequence Setup",
            bg="white",
            fg="black",
            font=("TkDefaultFont", 13),
        ).place(relx=0.5, y=10, anchor="n")

        tk.Label(
            background,
            text="Click on the part of the sequence and click Add.",
            bg="white",
            fg="#333333",
            anchor="w",
        ).place(x=10, y=40)

        self.command_list = tk.Listbox(
            background,
            height=8,
            exportselection=False,
            activestyle="dotbox",
        )
        for command in self.COMMANDS:
            self.command_list.insert("end", command["label"])
        self.command_list.place(x=10, y=64, width=380, height=142)
        self.command_list.bind("<ButtonPress-1>", self._start_palette_drag)
        self.command_list.bind("<Double-Button-1>", self._add_selected_command)

        self.add_button = ttk.Button(
            background,
            text="Add Selected",
            command=self._add_selected_command,
        )
        self.add_button.place(x=10, y=212, width=110)

        tk.Label(
            background,
            text="Sequence (drag rows to reorder)",
            bg="white",
            fg="black",
        ).place(x=10, y=245)
        self.sequence_tree = ttk.Treeview(
            background,
            columns=("number", "command", "parameters"),
            show="headings",
            selectmode="browse",
            height=8,
        )
        self.sequence_tree.heading("number", text="#")
        self.sequence_tree.heading("command", text="Command")
        self.sequence_tree.heading("parameters", text="Parameters")
        self.sequence_tree.column("number", width=32, stretch=False, anchor="center")
        self.sequence_tree.column("command", width=190, stretch=False)
        self.sequence_tree.column("parameters", width=150)
        self.sequence_tree.place(x=10, y=269, width=380, height=172)
        self.sequence_tree.bind("<ButtonPress-1>", self._start_sequence_drag)
        self.sequence_tree.bind("<<TreeviewSelect>>", self._on_sequence_selection)

        self.parameter_title = tk.Label(
            background,
            text="Selected command parameters",
            bg="white",
            fg="black",
        )
        self.parameter_title.place(x=10, y=450)
        self.argument_labels = [
            tk.Label(background, text="", bg="white", fg="black"),
            tk.Label(background, text="", bg="white", fg="black"),
        ]
        self.argument_entries = [
            ttk.Entry(background, width=15),
            ttk.Entry(background, width=15),
        ]
        for index, (label, entry) in enumerate(
            zip(self.argument_labels, self.argument_entries)
        ):
            x_position = 10 + index * 190
            label.place(x=x_position, y=474)
            entry.place(x=x_position, y=496, width=170)

        self.apply_button = ttk.Button(
            background,
            text="Apply Parameters",
            command=self._apply_parameters,
        )
        self.apply_button.place(x=10, y=528, width=130)
        self.delete_button = ttk.Button(
            background,
            text="Remove Selected",
            command=self._remove_selected,
        )
        self.delete_button.place(x=148, y=528, width=120)
        self.clear_button = ttk.Button(
            background,
            text="Clear",
            command=self._clear_sequence,
        )
        self.clear_button.place(x=276, y=528, width=70)

        self.run_button = ttk.Button(
            background,
            text="Run Sequence",
            command=self._run_sequence,
        )
        self.run_button.place(x=10, y=558, width=120)
        self.cancel_button = ttk.Button(
            background,
            text="Stop",
            command=self.cancel_sequence,
            state="disabled",
        )
        self.cancel_button.place(x=140, y=558, width=75)
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            background,
            textvariable=self.status_var,
            bg="white",
            fg="#333333",
            anchor="w",
        ).place(x=225, y=562, width=165)

        self.root.bind_all("<ButtonRelease-1>", self._finish_drag, add="+")
        return panel

    def show(self):
        self.app.close_all_panels()
        self.app.open_panel("Sequence Setup Panel")

    def _start_palette_drag(self, event):
        if self._is_running:
            return
        index = self.command_list.nearest(event.y)
        if index < 0 or index >= len(self.COMMANDS):
            self._drag_source = None
            return
        self.command_list.selection_clear(0, "end")
        self.command_list.selection_set(index)
        self._drag_source = ("palette", index)

    def _start_sequence_drag(self, event):
        if self._is_running:
            return
        action_id = self.sequence_tree.identify_row(event.y)
        self._drag_source = ("sequence", action_id) if action_id else None

    def _finish_drag(self, event):
        if self._drag_source is None or self._is_running:
            self._drag_source = None
            return

        target = self.root.winfo_containing(event.x_root, event.y_root)
        if target != self.sequence_tree:
            self._drag_source = None
            return

        source_type, source_value = self._drag_source
        self._drag_source = None
        y_position = event.y_root - self.sequence_tree.winfo_rooty()
        target_id = self.sequence_tree.identify_row(y_position)
        insert_index = len(self.sequence_tree.get_children())
        if target_id:
            target_index = self.sequence_tree.index(target_id)
            bounds = self.sequence_tree.bbox(target_id)
            if bounds and y_position > bounds[1] + bounds[3] / 2:
                target_index += 1
            insert_index = target_index

        if source_type == "palette":
            self._add_command(source_value, insert_index)
        elif source_value in self.sequence_tree.get_children():
            self._move_action(source_value, insert_index)

    def _add_selected_command(self, event=None):
        if self._is_running:
            return
        selection = self.command_list.curselection()
        if not selection:
            self.status_var.set("Select a command first.")
            return
        self._add_command(selection[0])

    def _add_command(self, command_index, insert_index=None):
        command = self.COMMANDS[command_index]
        action_id = f"step-{self._next_action_id}"
        self._next_action_id += 1
        action = {
            "command_index": command_index,
            "arguments": ["0"] * len(command["arguments"]),
        }
        self.actions[action_id] = action
        position = (
            "end"
            if insert_index is None
            else min(insert_index, len(self.sequence_tree.get_children()))
        )
        self.sequence_tree.insert(
            "",
            position,
            iid=action_id,
            values=(0, command["label"], self._format_arguments(command, action)),
        )
        self.sequence_tree.selection_set(action_id)
        self.sequence_tree.focus(action_id)
        self._refresh_sequence_numbers()
        self.status_var.set(f"Added {command['label']}.")

    def _move_action(self, action_id, insert_index):
        children = list(self.sequence_tree.get_children())
        old_index = children.index(action_id)
        target_index = min(insert_index, len(children))
        if old_index < target_index:
            target_index -= 1
        target_index = max(0, min(target_index, len(children) - 1))
        self.sequence_tree.move(action_id, "", target_index)
        self._refresh_sequence_numbers()

    def _on_sequence_selection(self, event=None):
        if self._selected_action_id:
            self._store_editor_values()

        selection = self.sequence_tree.selection()
        self._selected_action_id = selection[0] if selection else None
        if self._selected_action_id is None:
            self._clear_editor()
            return

        action = self.actions[self._selected_action_id]
        command = self.COMMANDS[action["command_index"]]
        for index, (label, entry) in enumerate(
            zip(self.argument_labels, self.argument_entries)
        ):
            if index < len(command["arguments"]):
                label.configure(text=command["arguments"][index])
                label.place(x=10 + index * 190, y=474)
                entry.configure(state="normal")
                entry.delete(0, "end")
                entry.insert(0, action["arguments"][index])
                entry.place(x=10 + index * 190, y=496, width=170)
            else:
                label.place_forget()
                entry.configure(state="disabled")
                entry.delete(0, "end")
                entry.place_forget()

    def _clear_editor(self):
        self._selected_action_id = None
        for label, entry in zip(self.argument_labels, self.argument_entries):
            label.configure(text="")
            label.place_forget()
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.place_forget()

    def _store_editor_values(self):
        if self._selected_action_id not in self.actions:
            return
        action = self.actions[self._selected_action_id]
        command = self.COMMANDS[action["command_index"]]
        for index in range(len(command["arguments"])):
            action["arguments"][index] = self.argument_entries[index].get().strip()
        self._update_action_row(self._selected_action_id)

    def _apply_parameters(self):
        if self._selected_action_id is None:
            self.status_var.set("Select a sequence command first.")
            return
        self._store_editor_values()
        self.status_var.set("Parameters applied.")

    def _update_action_row(self, action_id):
        action = self.actions[action_id]
        command = self.COMMANDS[action["command_index"]]
        self.sequence_tree.item(
            action_id,
            values=(
                self.sequence_tree.index(action_id) + 1,
                command["label"],
                self._format_arguments(command, action),
            ),
        )

    @staticmethod
    def _format_arguments(command, action):
        return ", ".join(
            f"{name}={value}"
            for name, value in zip(command["arguments"], action["arguments"])
        )

    def _refresh_sequence_numbers(self):
        for index, action_id in enumerate(self.sequence_tree.get_children(), start=1):
            values = list(self.sequence_tree.item(action_id, "values"))
            values[0] = index
            self.sequence_tree.item(action_id, values=values)

    def _remove_selected(self):
        if self._is_running:
            return
        selection = self.sequence_tree.selection()
        if not selection:
            return
        action_id = selection[0]
        self.sequence_tree.delete(action_id)
        self.actions.pop(action_id, None)
        self._clear_editor()
        self._refresh_sequence_numbers()
        self.status_var.set("Command removed.")

    def _clear_sequence(self):
        if self._is_running:
            return
        self.sequence_tree.delete(*self.sequence_tree.get_children())
        self.actions.clear()
        self._clear_editor()
        self.status_var.set("Sequence cleared.")

    def _run_sequence(self):
        if self._is_running:
            return
        if not self.app.hardware_controls_available():
            messagebox.showwarning(
                "Hardware Unavailable",
                "A scan is using the hardware. Try again when it has finished.",
                parent=self.root,
            )
            return

        if self._selected_action_id:
            self._store_editor_values()
        action_ids = self.sequence_tree.get_children()
        if not action_ids:
            messagebox.showwarning(
                "Empty Sequence",
                "Add at least one command before running the sequence.",
                parent=self.root,
            )
            return

        try:
            actions = [
                self._prepare_action(self.actions[action_id])
                for action_id in action_ids
            ]
        except ValueError as exc:
            messagebox.showwarning(
                "Invalid Command Parameters",
                str(exc),
                parent=self.root,
            )
            return

        self._is_running = True
        self._cancel_event.clear()
        self._set_running_controls(True)
        self.status_var.set("Starting sequence...")
        self.app.disable_buttons()
        threading.Thread(
            target=self._run_sequence_worker,
            args=(actions,),
            name="hardware-command-sequence",
            daemon=True,
        ).start()

    def _prepare_action(self, action):
        command = self.COMMANDS[action["command_index"]]
        values = []
        for label, value, value_type in zip(
            command["arguments"],
            action["arguments"],
            command["types"],
        ):
            try:
                values.append(value_type(value))
            except ValueError as exc:
                raise ValueError(
                    f"{command['label']}: enter a valid value for {label}."
                ) from exc
        return {
            "device": command["device"],
            "operation": command["operation"],
            "arguments": values,
            "label": command["label"],
        }

    def _run_sequence_worker(self, actions):
        error_message = None
        canceled = False
        try:
            for index, action in enumerate(actions, start=1):
                if self._cancel_event.is_set():
                    canceled = True
                    break
                self.app.call_on_ui_thread(
                    self.status_var.set,
                    f"Running {index}/{len(actions)}: {action['label']}",
                )
                self._execute_action(action)
        except Exception as exc:
            canceled = self._cancel_event.is_set()
            if not canceled:
                error_message = str(exc)
                try:
                    self.app.stage.stop_all()
                except Exception as stop_error:
                    error_message += f"\nStage stop failed: {stop_error}"
                try:
                    self.app.thor_controller.stop_all()
                except Exception as stop_error:
                    error_message += f"\nThor stop failed: {stop_error}"

        self.app.call_on_ui_thread(
            self._finish_sequence,
            canceled,
            error_message,
        )

    def _execute_action(self, action):
        if not self.app.hardware_controls_available():
            raise RuntimeError("Hardware became unavailable during the sequence.")

        controller = (
            self.app.stage if action["device"] == "stage" else self.app.thor_controller
        )
        operation = action["operation"]
        arguments = action["arguments"]

        if action["device"] == "stage" and operation == "move_xy":
            moved = controller.move_to_xy(
                *arguments,
                cancel_check=self._cancel_event.is_set,
            )
            if not moved:
                raise RuntimeError("The stage rejected the XY move.")
        elif action["device"] == "stage" and operation == "move_z":
            moved = controller.move_to_z(
                *arguments,
                cancel_check=self._cancel_event.is_set,
            )
            if not moved:
                raise RuntimeError("The stage rejected the Z move.")
        else:
            getattr(controller, operation)(*arguments)

    def cancel_sequence(self, show_errors=True):
        if not self._is_running:
            return
        self._cancel_event.set()
        self.status_var.set("Stopping sequence...")
        errors = []
        for controller, label in (
            (self.app.stage, "Stage"),
            (self.app.thor_controller, "Thor"),
        ):
            try:
                controller.stop_all()
            except Exception as exc:
                errors.append(f"{label}: {exc}")
        if errors and show_errors:
            messagebox.showerror(
                "Stop Failed",
                "Could not stop all motion:\n\n" + "\n".join(errors),
                parent=self.root,
            )

    def _finish_sequence(self, canceled, error_message):
        self._is_running = False
        self._set_running_controls(False)
        self.app.enable_buttons()
        if error_message:
            self.status_var.set("Sequence failed.")
            messagebox.showerror(
                "Sequence Failed",
                error_message,
                parent=self.root,
            )
        elif canceled:
            self.status_var.set("Sequence stopped.")
        else:
            self.status_var.set("Sequence complete.")

    def _set_running_controls(self, running):
        widget_state = "disabled" if running else "normal"
        self.command_list.configure(state=widget_state)
        if running:
            self.sequence_tree.state(["disabled"])
        else:
            self.sequence_tree.state(["!disabled"])
        self.add_button.configure(state=widget_state)
        self.apply_button.configure(state=widget_state)
        self.delete_button.configure(state=widget_state)
        self.clear_button.configure(state=widget_state)
        self.run_button.configure(state=widget_state)
        self.cancel_button.configure(state="normal" if running else "disabled")
        for entry in self.argument_entries:
            entry.configure(state="disabled" if running else "normal")
