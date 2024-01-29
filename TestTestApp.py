"""..."""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import io
import contextlib
import pytest
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from web_scrapping import FromageWEB

class TestTestApp:
    """..."""
    def __init__(self, master):
        self.master = master
        self.master.title("Application de Test")
        ttk.Button(self.master, text="Afficher les Résultats des Tests",
                   command=self.afficher_resultats_tests).pack(pady=10)
        ttk.Button(self.master, text="Mettre à Jour la Base de Données",
                   command=self.mise_a_jour_base_de_donnees).pack(pady=10)
        ttk.Button(self.master, text="Afficher le Diagramme en Camembert",
                   command=self.afficher_diagramme_camembert).pack(pady=10)
        ttk.Button(self.master, text="Quitter", command=self.quitter_application).pack(pady=10)

    def afficher_resultats_tests(self):
        """..."""
        results = self.executer_tests_et_capture_output()
        self.afficher_popup_resultats(results)

    def afficher_popup_resultats(self, results):
        """Affichage des résultats de test"""
        fenetre_popup = tk.Toplevel(self.master)
        fenetre_popup.title("Résultats des Tests")
        widget_texte = tk.Text(fenetre_popup, wrap="word", height=20, width=80)
        widget_texte.pack(padx=10, pady=10)
        for resultat in results:
            widget_texte.insert(tk.END, resultat)
            widget_texte.insert(tk.END, "\n" + "-" * 50 + "\n")
        widget_texte.config(state=tk.DISABLED)

    def mise_a_jour_base_de_donnees(self):
        """..."""
        messagebox.showinfo("Mise à Jour de la Base de Données",
                            "Base de Données Mise à Jour avec Succès !")

    def afficher_diagramme_camembert(self):
        """Construction et du camembert et de la famille 'autre'"""
        fromage_instance = FromageWEB('fromage.db')
        data = fromage_instance.give_display_data_family()
        fromage_instance.close_connection()
        if not data:
            messagebox.showinfo("Pas de Données",
                                "Aucune donnée à afficher pour le diagramme en camembert.")
            return
        modified_data = []

        single_family_data = ("Autre", 0)
        for item in data:
            if item[1] > 1:
                modified_data.append(item)
            else:
                single_family_data = ("Autre", single_family_data[1] + 1)
        modified_data.append(single_family_data)
        labels = [item[0] for item in modified_data]
        sizes = [item[1] for item in modified_data]
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        fenetre_diagramme_camembert = tk.Toplevel(self.master)
        fenetre_diagramme_camembert.title("Diagramme en Camembert")
        canvas = FigureCanvasTkAgg(fig, master=fenetre_diagramme_camembert)
        canvas.get_tk_widget().pack()

    def executer_tests_et_capture_output(self):
        """Capture et renvoie le résultat des tests pytest"""
        results = []
        capture_output = io.StringIO()
        with contextlib.redirect_stdout(capture_output):
            pytest.main(['-v'])
        results.append(capture_output.getvalue())
        return results

    def quitter_application(self):
        """Ferme l'application."""
        self.master.destroy()

if __name__ == "__main__":
    racine = tk.Tk()
    application = TestTestApp(racine)
    racine.protocol("WM_DELETE_WINDOW", application.quitter_application)
    racine.mainloop()
