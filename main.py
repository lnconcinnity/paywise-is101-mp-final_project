from scheduler import run, populate
from layout import layout

if __name__ == "__main__":
    content = layout()
    populate(content)
    run()