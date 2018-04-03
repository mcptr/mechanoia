BLOG_NAME = blog.mk

.PHONY: all clean generate

all: clean generate

generate:
	tree -T $(BLOG_NAME) -txD -H . > index.html
	tree -x -h -X > sitemap.xml
	date +%s > _meta.mtime.txt  # not a bug.

clean:
	@find . -name '*~' | xargs rm -rfv
