LESSC = node_modules/.bin/lessc
BOWER = node_modules/.bin/bower
TRACEUR = node_modules/.bin/traceur
UGLIFYJS = node_modules/.bin/uglifyjs
STDIOIFY = node_modules/.bin/stdioify
NPM_TOOLS = $(BOWER) $(TRACEUR) $(UGLIFYJS) $(LESSC) $(STDIOIFY)
JS_EXTERNAL = bower_components/jquery/dist/jquery.js \
			  bower_components/angular/angular.js
JS_EXTERNAL_MINIFIED=$(JS_EXTERNAL:bower_components/%.js=build/external/%.js)
BOWER_SOURCES = $(JS_EXTERNAL)
JS = $(shell find webapp/js -name "*.js")
JS_COMPILED = $(JS:webapp/js/%.js=build/js/%.js)

all: deps webapp_dist/bundle.js webapp_dist/index.html
deps: node_modules bower_components .pip_install

venv-3.4:
	pyvenv-3.4 $@

.pip_install: venv-3.4 requirements.txt dev-requirements.txt
	venv-3.4/bin/pip install -r dev-requirements.txt
	@touch .pip_install

node_modules: package.json
	npm install --silent
	@touch $@

bower_components: node_modules bower.json
	bower install
	@touch $@

$(NPM_TOOLS): node_modules
	@touch $@

$(BOWER_SOURCES): bower_components

# This is ridiculous:
# https://github.com/google/traceur-compiler/issues/628
TRACEUR_CMD=$(STDIOIFY) --command $(TRACEUR) --in-arg="--script" --out-arg="--out" --suffix=".js"

build/js/%.js: webapp/js/%.js $(STDIOIFY) $(TRACEUR) $(UGLIFYJS)
	@mkdir -p $(@D)
	cat $< | $(TRACEUR_CMD) | $(UGLIFYJS) > $@

build/external/%.js: bower_components/%.js $(UGLIFYJS)
	@mkdir -p $(@D)
	$(UGLIFYJS) $< > $@

webapp_dist:
	mkdir -p $@

webapp_dist/bundle.js: $(JS_EXTERNAL_MINIFIED) $(JS_COMPILED) webapp_dist
	cat $(JS_EXTERNAL_MINIFIED) $(JS_COMPILED) > $@

webapp_dist/index.html: webapp_dist webapp/index.html
	cp webapp/index.html webapp_dist/index.html

clean:
	rm -rf build webapp_dist

full_clean: clean
	rm -rf bower_components node_modules venv-* .pip_install

.PHONY: clean full_clean deps python_deps
