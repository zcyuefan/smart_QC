#!/usr/bin/env bash
# Use this script to start/stop/restart server.(not valid, just start as dev now)
# for example:
# "run.sh --sign=start --env=dev" or "run.sh -S start -E dev"
# "run.sh --sign=stop" or "run.sh /S stop"
# "run.sh --sign=restart --env=dev" or "run.sh -S restart -E dev"
@echo off
python ../manage.py runserver --settings=django_smart_QC.settings.dev