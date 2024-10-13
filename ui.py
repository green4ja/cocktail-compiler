import tkinter
import tkinter.messagebox
import customtkinter

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class IngredientsPage(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.label = customtkinter.CTkLabel(self, text="Ingredients", font=("Helvetica", 20, "bold"))
        self.label.pack(pady=20, padx=20)

class FunctionsPage(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.label = customtkinter.CTkLabel(self, text="Functions", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=20, padx=20)

        # Create buttons
        self.fetch_random_cocktail_button = customtkinter.CTkButton(self, text="Fetch Random Cocktail")
        self.select_random_stored_cocktail_button = customtkinter.CTkButton(self, text="Select Random Stored Cocktail")
        self.get_top_missing_ingredients_button = customtkinter.CTkButton(self, text="Get Top Missing Ingredients")

        # Pack buttons in a column
        self.fetch_random_cocktail_button.pack(pady=10)
        self.select_random_stored_cocktail_button.pack(pady=10)
        self.get_top_missing_ingredients_button.pack(pady=10)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("cocktail-compiler")
        self.geometry(f"{500}x{600}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="cocktail-compiler", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Functions", command=lambda: self.show_frame(FunctionsPage))
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Ingredients", command=lambda: self.show_frame(IngredientsPage))
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        self.appearance_mode_optionemenu.set("System")

        # create main frame for pages
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.frames = {}
        for F in (IngredientsPage, FunctionsPage):
            page_name = F.__name__
            frame = F(master=self.main_frame)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(FunctionsPage)

    def show_frame(self, page_class):
        frame = self.frames[page_class.__name__]
        frame.tkraise()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    app = App()
    app.mainloop()
