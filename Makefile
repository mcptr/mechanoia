.PHONY: all scss

SRC_SCSS = web/assets/scss
DIR_STATIC_CSS = static/gen/css


all: scss

scss:
	mkdir -p $(DIR_STATIC_CSS)
	python -mscss -C $(SRC_SCSS)/main.scss > $(DIR_STATIC_CSS)/main.css
