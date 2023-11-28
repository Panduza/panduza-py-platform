echo $COVERAGE


# CMD mkdir -p /etc/panduza/plugins/py; \


if [ "$COVERAGE" -eq "1" ]; then
    # echo "COVV"
    coverage run --data-file=/platform/.coverage /platform/panduza_platform/__main__.py
    coverage report -m
    # coverage html -d coverage_html
else
    python3.11 /platform/panduza_platform/__main__.py
fi

