import pytest
from vp_core.helpers.case_converter import to_camel

def test_to_camel():
    assert to_camel("snake_case") == "snakeCase"
    assert to_camel("hello_world_test") == "helloWorldTest"
    assert to_camel("alreadyCamel") == "alreadyCamel"
    assert to_camel("with_id") == "withId"

def test_benchmark_to_camel(benchmark):
    # Benchmark the to_camel function
    result = benchmark(to_camel, "some_complex_snake_case_string_for_benchmarking")
    assert result == "someComplexSnakeCaseStringForBenchmarking"
