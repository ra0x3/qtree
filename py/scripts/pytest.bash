#!/bin/bash

export $(cat .env | xargs) && pytest

