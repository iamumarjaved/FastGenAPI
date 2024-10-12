from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from src.core.config.config import settings
import os

# Setting up the TracerProvider
resource = Resource.create(attributes={"service.name": "my-fastapi-app"})

provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# Configure OTLP exporter (for HyperDX)
otlp_exporter = OTLPSpanExporter(
    endpoint="https://ingest.hyperdx.io", 
    headers={
        "x-hdx-auth-token": settings.hyperdx_api_key
    }
)

# Set up the processor and add it to the provider
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)
