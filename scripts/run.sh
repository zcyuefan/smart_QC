#!/usr/bin/env bash
# Use this script to start/stop/restart server.(not valid, just start as dev now)
# for example:
# "running.sh --sign=start --env=dev" or "running.sh -S start -E dev"
# "running.sh --sign=stop" or "running.sh /S stop"
# "running.sh --sign=restart --env=dev" or "running.sh -S restart -E dev"
@echo off
python ../manage.py runserver --settings=django_smart_QC.settings.dev