import sys
import types

try:
    from google import genai
    from google.genai import types as genai_types
except (ImportError, AttributeError):
    import google
    mock_genai = types.ModuleType("google.genai")
    mock_genai.Client = type("Client", (), {})
    mock_types = types.ModuleType("google.genai.types")
    mock_types.GenerateContentConfig = lambda **kwargs: kwargs
    mock_genai.types = mock_types
    google.genai = mock_genai
    sys.modules["google.genai"] = mock_genai
    sys.modules["google.genai.types"] = mock_types
