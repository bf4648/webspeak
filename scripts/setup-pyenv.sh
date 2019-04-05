#!/usr/bin/env bash

install_pyenv() {
	pyenv install -s 3.4.0
	pyenv virtualenv 3.4.0 web-speak-3.4.0
	pyenv activate web-speak-3.4.0
	pyenv rehash
	# pip3 install aiohttp==0.14.4
}

main() {
	install_pyenv
}
