import tkinter as tk
import math
import re


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")

        self.expression = ""
        self.display_expr = ""

        self.mode = "standard"
        self.is_dark = True

        self.buttons = []
        self.error_state = False
        self.just_evaluated = False

        self.just_opened_func = False

        self.root.geometry("460x500")
        self.root.minsize(460, 500)

        self.build_ui()
        self.bind_keys()
        self.apply_theme()

    def reset_grid(self, cols):
        for c in range(10):
            self.buttons_frame.grid_columnconfigure(c, weight=0, uniform="")

        for c in range(cols):
            self.buttons_frame.grid_columnconfigure(c, weight=1, uniform="grid")

        for r in range(5):
            self.buttons_frame.grid_rowconfigure(r, weight=1, uniform="grid")

    def fact(self, x):
        try:
            return math.factorial(int(x))
        except:
            return 0

    def npr(self, n, r):
        try:
            n = int(n)
            r = int(r)
            if r < 0 or n < 0 or r > n:
                return 0
            return math.factorial(n) // math.factorial(n - r)
        except:
            return 0

    def format_indian(self, num):
        try:
            s = str(num)

            if "e" in s or "E" in s:
                return s

            if "." in s:
                whole, dec = s.split(".")
            else:
                whole, dec = s, ""

            neg = whole.startswith("-")

            if neg:
                whole = whole[1:]

            if len(whole) <= 3:
                result = whole
            else:
                last3 = whole[-3:]
                rest = whole[:-3]

                parts = []
                while len(rest) > 2:
                    parts.insert(0, rest[-2:])
                    rest = rest[:-2]

                if rest:
                    parts.insert(0, rest)

                result = ",".join(parts) + "," + last3

            if neg:
                result = "-" + result

            if dec:
                result += "." + dec

            return result

        except:
            return str(num)

    def build_ui(self):
        self.main = tk.Frame(self.root)
        self.main.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(self.main, width=130)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.mode_label = tk.Label(self.sidebar, text="Mode: Standard",
                                    font=("Segoe UI", 11, "bold"))
        self.mode_label.pack(pady=10)

        self.mode_var = tk.StringVar(value="standard")

        self.mode_menu = tk.OptionMenu(
            self.sidebar,
            self.mode_var,
            "Standard Mode",
            "Scientific Mode",
            command=self.switch_mode
        )
        self.mode_menu.pack(fill="x", pady=5)

        self.theme_btn = tk.Button(
            self.sidebar,
            text="Light Mode",
            command=self.toggle_theme,
            bd=0
        )
        self.theme_btn.pack(fill="x", pady=5)

        self.history_frame = tk.Frame(self.sidebar)
        self.history_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.history_scrollbar = tk.Scrollbar(self.history_frame)
        self.history_scrollbar.pack(side="right", fill="y")

        self.history_box = tk.Listbox(
            self.history_frame,
            height=10,
            yscrollcommand=self.history_scrollbar.set,
            bd=0,
            highlightthickness=0
        )
        self.history_box.pack(side="left", fill="both", expand=True)

        self.history_scrollbar.config(command=self.history_box.yview)

        self.clear_history_btn = tk.Button(
            self.sidebar,
            text="Clear History",
            command=self.clear_history,
            bd=0
        )
        self.clear_history_btn.pack(fill="x", pady=5)

        self.center = tk.Frame(self.main)
        self.center.pack(side="left", fill="both", expand=True)

        self.display_frame = tk.Frame(self.center)
        self.display_frame.pack(fill="x", padx=10, pady=5)

        self.display_label = tk.Label(
            self.display_frame,
            text="0",
            font=("Segoe UI", 22),
            anchor="e",
            padx=5,
            pady=10
        )
        self.display_label.pack(fill="x")

        self.buttons_frame = tk.Frame(self.center)
        self.buttons_frame.pack(expand=True, fill="both", padx=4, pady=2)

        self.draw_buttons()

    def draw_buttons(self):
        for w in self.buttons_frame.winfo_children():
            w.destroy()

        self.buttons.clear()

        base = [
            ['C', 'x²', 'x³', '%'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=', '/']
        ]

        sci = [
            ['sin', 'cos', 'tan', 'floor', 'x^y'],
            ['asin', 'acos', 'atan', 'ceil', 'ln'],
            ['sinh', 'cosh', 'tanh', 'abs', 'exp'],
            ['log', 'nPr', 'ln', 'sqrt', 'x⁻¹'],
            ['phi', 'pi', 'e', '!', 'mod']
        ]

        if self.mode == "standard":
            self.reset_grid(4)
            for r, row in enumerate(base):
                for c, val in enumerate(row):
                    self.create_btn(val, r, c)

        else:
            self.reset_grid(9)
            for r, row in enumerate(base):
                for c, val in enumerate(row):
                    self.create_btn(val, r, c)

            for r, row in enumerate(sci):
                for c, val in enumerate(row):
                    self.create_btn(val, r, 4 + c)

    def create_btn(self, text, r, c):
        btn = tk.Button(
            self.buttons_frame,
            text=text,
            font=("Segoe UI", 11),
            bd=0,
            relief="flat",
            command=lambda t=text: self.on_click(t),
            cursor="hand2"
        )
        btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
        self.buttons.append(btn)

    def add_func(self, name):
        self.expression += f"{name}("
        self.display_expr += name + " "
        self.just_opened_func = True

    def on_click(self, char):

        if char == "C":
            self.clear_all()
            return

        if self.error_state:
            return

        if self.just_evaluated and char.isdigit():
            self.expression = ""
            self.display_expr = ""
            self.just_evaluated = False

        try:

            if char == "=":

                open_b = self.expression.count("(")
                close_b = self.expression.count(")")

                self.expression += ")" * (open_b - close_b)

                result = eval(
                    self.expression,
                    {"__builtins__": None},
                    {
                        "math": math,
                        "abs": abs,
                        "nPr": self.npr,
                        "fact": self.fact,
                        "sin": math.sin,
                        "cos": math.cos,
                        "tan": math.tan,
                        "asin": math.asin,
                        "acos": math.acos,
                        "atan": math.atan,
                        "sinh": math.sinh,
                        "cosh": math.cosh,
                        "tanh": math.tanh,
                        "log": math.log10,
                        "ln": math.log,
                        "exp": math.exp,
                        "floor": math.floor,
                        "ceil": math.ceil,
                        "sqrt": math.sqrt
                    }
                )

                formatted = self.format_indian(result)

                self.history_box.insert(
                    tk.END,
                    f"{self.display_expr} = {formatted}"
                )

                self.expression = str(result)
                self.display_expr = str(result)

            elif char in "0123456789":
                self.expression += char
                self.display_expr += char

            elif char in "+-*/.%":
                self.expression += char
                self.display_expr += char

            elif char == "pi":
                self.expression += str(math.pi)
                self.display_expr += "π"

            elif char == "e":
                self.expression += str(math.e)
                self.display_expr += "e"

            elif char == "x²":
                self.expression += "**2"
                self.display_expr += "²"

            elif char == "x³":
                self.expression += "**3"
                self.display_expr += "³"

            elif char == "sqrt":
                self.add_func("sqrt")

            elif char == "!":
                self.expression = f"fact({self.expression})"
                self.display_expr += "!"

            elif char in ["sin","cos","tan","asin","acos","atan",
                          "sinh","cosh","tanh","log","ln",
                          "floor","ceil"]:
                self.add_func(char)

            self.update_display()

        except:
            self.expression = ""
            self.display_expr = "Error"
            self.error_state = True
            self.update_display()

    def update_display(self):
        self.display_label.config(
            text=self.display_expr if self.display_expr else "0"
        )

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.theme_btn.config(
            text="Light Mode" if self.is_dark else "Dark Mode"
        )
        self.apply_theme()

    def apply_theme(self):
        self.bg = "#000000" if self.is_dark else "#f5f7ff"
        self.btn = "#1a1a1a" if self.is_dark else "#e3e8f5"
        self.fg = "#ffffff" if self.is_dark else "#1b1f2a"

        self.root.config(bg=self.bg)
        self.main.config(bg=self.bg)
        self.sidebar.config(bg=self.bg)
        self.center.config(bg=self.bg)
        self.display_frame.config(bg=self.bg)
        self.display_label.config(bg=self.bg, fg=self.fg)

        self.history_frame.config(bg=self.bg)
        self.history_box.config(bg=self.btn, fg=self.fg)

        self.clear_history_btn.config(bg=self.btn, fg=self.fg)
        self.theme_btn.config(bg=self.btn, fg=self.fg)
        self.mode_menu.config(bg=self.btn, fg=self.fg)
        self.mode_label.config(bg=self.bg, fg=self.fg)

        for b in self.buttons:
            b.config(bg=self.btn, fg=self.fg)

    def switch_mode(self, mode):
        self.mode_label.config(text=f"Mode: {self.mode.capitalize()}")
        self.mode = "standard" if "Standard" in mode else "scientific"
        self.clear_all()

        target = 460 if self.mode == "standard" else 750

        self.draw_buttons()
        self.apply_theme()

        self.root.geometry(f"{target}x500")

    def clear_all(self):
        self.expression = ""
        self.display_expr = ""
        self.error_state = False
        self.just_evaluated = False
        self.update_display()

    def clear_history(self):
        self.history_box.delete(0, tk.END)

    def bind_keys(self):
        self.root.bind("<Key>", self.key_handler)

    def key_handler(self, event):
        key = event.keysym
        char = event.char

        if key == "Return":
            self.on_click("=")
        elif key == "BackSpace":
            self.expression = self.expression[:-1]
            self.display_expr = self.display_expr[:-1]
            self.update_display()
        elif key == "Escape":
            self.clear_all()
        elif char.isdigit() or char in "+-*/.%":
            self.on_click(char)


class FixedCalculator(Calculator):
    def normalize_expression(self, expr):
        funcs = ["sin","cos","tan","asin","acos","atan",
                 "sinh","cosh","tanh","log","ln","sqrt",
                 "floor","ceil","exp"]

        i = 0
        out = ""

        while i < len(expr):
            matched = False
            for f in funcs:
                if expr[i:i+len(f)] == f:
                    out += f + "("
                    i += len(f)
                    matched = True
                    break

            if not matched:
                out += expr[i]
                i += 1

        return out

    def on_click(self, char):
        super().on_click(char)

        if char == "=" and not self.error_state:
            try:
                self.expression = self.normalize_expression(self.expression)

                open_b = self.expression.count("(")
                close_b = self.expression.count(")")

                self.expression += ")" * (open_b - close_b)

            except:
                pass


def attach_degree_toggle(calc):
    calc.angle_mode = "RAD"

    btn = tk.Button(
        calc.sidebar,
        text="Mode: RAD",
        bd=0,
        command=lambda: toggle(calc, btn)
    )
    btn.pack(fill="x", pady=5)

    def toggle(calc, btn):
        calc.angle_mode = "DEG" if calc.angle_mode == "RAD" else "RAD"
        btn.config(text=f"Mode: {calc.angle_mode}")

    original_sin = math.sin
    original_cos = math.cos
    original_tan = math.tan
    original_asin = math.asin
    original_acos = math.acos
    original_atan = math.atan

    def sin(x):
        return original_sin(math.radians(x)) if calc.angle_mode == "DEG" else original_sin(x)

    def cos(x):
        return original_cos(math.radians(x)) if calc.angle_mode == "DEG" else original_cos(x)

    def tan(x):
        return original_tan(math.radians(x)) if calc.angle_mode == "DEG" else original_tan(x)

    math.sin = sin
    math.cos = cos
    math.tan = tan
    math.asin = lambda x: math.degrees(original_asin(x)) if calc.angle_mode == "DEG" else original_asin(x)
    math.acos = lambda x: math.degrees(original_acos(x)) if calc.angle_mode == "DEG" else original_acos(x)
    math.atan = lambda x: math.degrees(original_atan(x)) if calc.angle_mode == "DEG" else original_atan(x)

# ---------------- INDIAN NUMBER SYSTEM SAFE DISPLAY PATCH ---------------- #

_original_update_display = Calculator.update_display

def _patched_update_display(self):
    try:
        text = self.display_expr if self.display_expr else "0"

        # Only format standalone numbers safely
        parts = re.split(r'(\D)', text)  # keep operators separate

        def format_if_number(x):
            if re.fullmatch(r'\d+(\.\d+)?', x):
                return self.format_indian(x)
            return x

        formatted_text = "".join(format_if_number(p) for p in parts)

        self.display_label.config(text=formatted_text)

    except:
        _original_update_display(self)

Calculator.update_display = _patched_update_display


if __name__ == "__main__":
    root = tk.Tk()
    calc = FixedCalculator(root)
    attach_degree_toggle(calc)
    root.mainloop()
