import gradio as gr
from gradio_ui.layout import create_layout

def main():
    layout = create_layout()
    layout.launch()

if __name__ == "__main__":
    main()