import tkinter as tk
from tkinter import ttk, messagebox

class Proceso:
    def __init__(self, id, llegada, burst, memoria, prioridad=0):
        self.id = id
        self.llegada = llegada
        self.burst = burst
        self.memoria = memoria
        self.prioridad = prioridad
        self.tiempo_espera = 0
        self.tiempo_retorno = 0

class SimuladorProcesos:
    def __init__(self):
        self.procesos = []

    def fcfs(self, procesos):
        tiempo_actual = 0
        for p in sorted(procesos, key=lambda x: x.llegada):
            p.tiempo_espera = max(0, tiempo_actual - p.llegada)
            tiempo_actual = max(tiempo_actual, p.llegada) + p.burst
            p.tiempo_retorno = tiempo_actual - p.llegada
        return procesos

    def sjf(self, procesos):
        tiempo_actual = 0
        cola = sorted(procesos, key=lambda x: (x.llegada, x.burst))
        ejecutados = []
        while cola:
            p = next((p for p in cola if p.llegada <= tiempo_actual), None)
            if not p:
                tiempo_actual += 1
                continue
            p.tiempo_espera = tiempo_actual - p.llegada
            tiempo_actual += p.burst
            p.tiempo_retorno = tiempo_actual - p.llegada
            cola.remove(p)
            ejecutados.append(p)
        return ejecutados

    def round_robin(self, procesos, quantum):
        tiempo_actual = 0
        cola = list(procesos)
        tiempos_restantes = {p.id: p.burst for p in procesos}
        ejecucion = []
        while cola:
            p = cola.pop(0)
            ejecucion.append(p)
            if tiempos_restantes[p.id] > quantum:
                tiempo_actual += quantum
                tiempos_restantes[p.id] -= quantum
                cola.append(p)
            else:
                tiempo_actual += tiempos_restantes[p.id]
                p.tiempo_retorno = tiempo_actual - p.llegada
                p.tiempo_espera = p.tiempo_retorno - p.burst
                tiempos_restantes[p.id] = 0
        return procesos

    def prioridad(self, procesos):
        tiempo_actual = 0
        cola = sorted(procesos, key=lambda x: (x.llegada, x.prioridad))
        ejecutados = []
        while cola:
            p = next((p for p in cola if p.llegada <= tiempo_actual), None)
            if not p:
                tiempo_actual += 1
                continue
            p.tiempo_espera = tiempo_actual - p.llegada
            tiempo_actual += p.burst
            p.tiempo_retorno = tiempo_actual - p.llegada
            cola.remove(p)
            ejecutados.append(p)
        return ejecutados

    def fms(self, procesos, memoria_total):
        tiempo_actual = 0
        cola = sorted(procesos, key=lambda x: x.llegada)
        ejecutados = []
        memoria_disponible = memoria_total
        while cola:
            p = next((p for p in cola if p.llegada <= tiempo_actual and p.memoria <= memoria_disponible), None)
            if not p:
                tiempo_actual += 1
                continue
            memoria_disponible -= p.memoria
            p.tiempo_espera = tiempo_actual - p.llegada
            tiempo_actual += p.burst
            p.tiempo_retorno = tiempo_actual - p.llegada
            memoria_disponible += p.memoria
            cola.remove(p)
            ejecutados.append(p)
        return ejecutados

class App:
    def __init__(self, root):
        self.root = root
        self.sim = SimuladorProcesos()
        self.root.title("Simulador de Planificación de Procesos")
        self.procesos = []
        self.setup_ui()

    def setup_ui(self):
        frame_input = ttk.LabelFrame(self.root, text="Agregar Proceso")
        frame_input.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(frame_input, text="ID:").grid(row=0, column=0)
        ttk.Label(frame_input, text="Llegada:").grid(row=0, column=2)
        ttk.Label(frame_input, text="Burst:").grid(row=1, column=0)
        ttk.Label(frame_input, text="Memoria:").grid(row=1, column=2)
        ttk.Label(frame_input, text="Prioridad:").grid(row=2, column=0)

        self.e_id = ttk.Entry(frame_input, width=5)
        self.e_llegada = ttk.Entry(frame_input, width=5)
        self.e_burst = ttk.Entry(frame_input, width=5)
        self.e_memoria = ttk.Entry(frame_input, width=5)
        self.e_prioridad = ttk.Entry(frame_input, width=5)

        self.e_id.grid(row=0, column=1)
        self.e_llegada.grid(row=0, column=3)
        self.e_burst.grid(row=1, column=1)
        self.e_memoria.grid(row=1, column=3)
        self.e_prioridad.grid(row=2, column=1)

        ttk.Button(frame_input, text="Agregar", command=self.agregar_proceso).grid(row=2, column=2, columnspan=2)

        frame_controls = ttk.LabelFrame(self.root, text="Configuración")
        frame_controls.grid(row=1, column=0, padx=10, pady=5)

        ttk.Label(frame_controls, text="Algoritmo:").grid(row=0, column=0)
        self.combo_algoritmo = ttk.Combobox(frame_controls, values=["FCFS", "SJF", "Round Robin", "Prioridad", "FMS"])
        self.combo_algoritmo.grid(row=0, column=1)
        self.combo_algoritmo.current(0)

        ttk.Label(frame_controls, text="Quantum:").grid(row=1, column=0)
        self.e_quantum = ttk.Entry(frame_controls, width=5)
        self.e_quantum.grid(row=1, column=1)
        ttk.Label(frame_controls, text="Memoria total:").grid(row=2, column=0)
        self.e_memoria_total = ttk.Entry(frame_controls, width=5)
        self.e_memoria_total.grid(row=2, column=1)

        ttk.Button(frame_controls, text="Simular", command=self.simular).grid(row=3, column=0, columnspan=2)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Espera", "Retorno"), show="headings")
        self.tree.grid(row=0, column=1, rowspan=3, padx=10, pady=10)
        self.tree.heading("ID", text="Proceso")
        self.tree.heading("Espera", text="Tiempo Espera")
        self.tree.heading("Retorno", text="Tiempo Retorno")

    def agregar_proceso(self):
        try:
            p = Proceso(
                int(self.e_id.get()),
                int(self.e_llegada.get()),
                int(self.e_burst.get()),
                int(self.e_memoria.get()),
                int(self.e_prioridad.get() or 0)
            )
            self.procesos.append(p)
            messagebox.showinfo("Éxito", f"Proceso {p.id} agregado.")
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos")

    def simular(self):
        algoritmo = self.combo_algoritmo.get()
        quantum = int(self.e_quantum.get() or 2)
        memoria_total = int(self.e_memoria_total.get() or 1024)

        for p in self.procesos:
            p.tiempo_espera = p.tiempo_retorno = 0

        if algoritmo == "FCFS":
            resultados = self.sim.fcfs(self.procesos)
        elif algoritmo == "SJF":
            resultados = self.sim.sjf(self.procesos)
        elif algoritmo == "Round Robin":
            resultados = self.sim.round_robin(self.procesos, quantum)
        elif algoritmo == "Prioridad":
            resultados = self.sim.prioridad(self.procesos)
        elif algoritmo == "FMS":
            resultados = self.sim.fms(self.procesos, memoria_total)

        self.tree.delete(*self.tree.get_children())
        total_espera = total_retorno = 0
        for p in resultados:
            self.tree.insert('', 'end', values=(p.id, p.tiempo_espera, p.tiempo_retorno))
            total_espera += p.tiempo_espera
            total_retorno += p.tiempo_retorno

        n = len(resultados)
        promedio_espera = total_espera / n if n else 0
        promedio_retorno = total_retorno / n if n else 0
        messagebox.showinfo("Promedios", f"Promedio Espera: {promedio_espera:.2f}\nPromedio Retorno: {promedio_retorno:.2f}")

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
