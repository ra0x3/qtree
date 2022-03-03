#!/bin/bash

bash scripts/lint.bash && bash scripts/mypy.bash && bash scripts/pytest.bash
