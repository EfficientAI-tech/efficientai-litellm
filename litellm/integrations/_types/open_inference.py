from enum import Enum


class SpanAttributes:
    OUTPUT_VALUE = "output.value"
    OUTPUT_MIME_TYPE = "output.mime_type"
    """
    The type of output.value. If unspecified, the type is plain text by default.
    If type is JSON, the value is a string representing a JSON object.
    """
    INPUT_VALUE = "input.value"
    INPUT_MIME_TYPE = "input.mime_type"
    """
    The type of input.value. If unspecified, the type is plain text by default.
    If type is JSON, the value is a string representing a JSON object.
    """

    EMBEDDING_EMBEDDINGS = "embedding.embeddings"
    """
    A list of objects containing embedding data, including the vector and represented piece of text.
    """
    EMBEDDING_MODEL_NAME = "embedding.model_name"
    """
    The name of the embedding model.
    """

    LLM_FUNCTION_CALL = "llm.function_call"
    """
    For models and APIs that support function calling. Records attributes such as the function
    name and arguments to the called function.
    """
    LLM_INVOCATION_PARAMETERS = "llm.invocation_parameters"
    """
    Invocation parameters passed to the LLM or API, such as the model name, temperature, etc.
    """
    LLM_INPUT_MESSAGES = "llm.input_messages"
    """
    Messages provided to a chat API.
    """
    LLM_OUTPUT_MESSAGES = "llm.output_messages"
    """
    Messages received from a chat API.
    """
    LLM_MODEL_NAME = "llm.model_name"
    """
    The name of the model being used.
    """
    LLM_PROMPTS = "llm.prompts"
    """
    Prompts provided to a completions API.
    """
    LLM_PROMPT_TEMPLATE = "llm.prompt_template.template"
    """
    The prompt template as a Python f-string.
    """
    LLM_PROMPT_TEMPLATE_VARIABLES = "llm.prompt_template.variables"
    """
    A list of input variables to the prompt template.
    """
    LLM_PROMPT_TEMPLATE_VERSION = "llm.prompt_template.version"
    """
    The version of the prompt template being used.
    """
    LLM_TOKEN_COUNT_PROMPT = "llm.token_count.prompt"
    """
    Number of tokens in the prompt.
    """
    LLM_TOKEN_COUNT_COMPLETION = "llm.token_count.completion"
    """
    Number of tokens in the completion.
    """
    LLM_TOKEN_COUNT_TOTAL = "llm.token_count.total"
    """
    Total number of tokens, including both prompt and completion.
    """

    TOOL_NAME = "tool.name"
    """
    Name of the tool being used.
    """
    TOOL_DESCRIPTION = "tool.description"
    """
    Description of the tool's purpose, typically used to select the tool.
    """
    TOOL_PARAMETERS = "tool.parameters"
    """
    Parameters of the tool represented a dictionary JSON string, e.g.
    see https://platform.openai.com/docs/guides/gpt/function-calling
    """

    RETRIEVAL_DOCUMENTS = "retrieval.documents"

    METADATA = "metadata"
    """
    Metadata attributes are used to store user-defined key-value pairs.
    For example, LangChain uses metadata to store user-defined attributes for a chain.
    """

    TAG_TAGS = "tag.tags"
    """
    Custom categorical tags for the span.
    """

    OPENINFERENCE_SPAN_KIND = "openinference.span.kind"

    SESSION_ID = "session.id"
    """
    The id of the session
    """
    USER_ID = "user.id"
    """
    The id of the user
    """


class MessageAttributes:
    """
    Attributes for a message sent to or from an LLM
    """

    MESSAGE_ROLE = "message.role"
    """
    The role of the message, such as "user", "agent", "function".
    """
    MESSAGE_CONTENT = "message.content"
    """
    The content of the message to or from the llm, must be a string.
    """
    MESSAGE_CONTENTS = "message.contents"
    """
    The message contents to the llm, it is an array of
    `message_content` prefixed attributes.
    """
    MESSAGE_NAME = "message.name"
    """
    The name of the message, often used to identify the function
    that was used to generate the message.
    """
    MESSAGE_TOOL_CALLS = "message.tool_calls"
    """
    The tool calls generated by the model, such as function calls.
    """
    MESSAGE_FUNCTION_CALL_NAME = "message.function_call_name"
    """
    The function name that is a part of the message list.
    This is populated for role 'function' or 'agent' as a mechanism to identify
    the function that was called during the execution of a tool.
    """
    MESSAGE_FUNCTION_CALL_ARGUMENTS_JSON = "message.function_call_arguments_json"
    """
    The JSON string representing the arguments passed to the function
    during a function call.
    """


class MessageContentAttributes:
    """
    Attributes for the contents of user messages sent to an LLM.
    """

    MESSAGE_CONTENT_TYPE = "message_content.type"
    """
    The type of the content, such as "text" or "image".
    """
    MESSAGE_CONTENT_TEXT = "message_content.text"
    """
    The text content of the message, if the type is "text".
    """
    MESSAGE_CONTENT_IMAGE = "message_content.image"
    """
    The image content of the message, if the type is "image".
    An image can be made available to the model by passing a link to
    the image or by passing the base64 encoded image directly in the
    request.
    """


class ImageAttributes:
    """
    Attributes for images
    """

    IMAGE_URL = "image.url"
    """
    An http or base64 image url
    """


class DocumentAttributes:
    """
    Attributes for a document.
    """

    DOCUMENT_ID = "document.id"
    """
    The id of the document.
    """
    DOCUMENT_SCORE = "document.score"
    """
    The score of the document
    """
    DOCUMENT_CONTENT = "document.content"
    """
    The content of the document.
    """
    DOCUMENT_METADATA = "document.metadata"
    """
    The metadata of the document represented as a dictionary
    JSON string, e.g. `"{ 'title': 'foo' }"`
    """


class RerankerAttributes:
    """
    Attributes for a reranker
    """

    RERANKER_INPUT_DOCUMENTS = "reranker.input_documents"
    """
    List of documents as input to the reranker
    """
    RERANKER_OUTPUT_DOCUMENTS = "reranker.output_documents"
    """
    List of documents as output from the reranker
    """
    RERANKER_QUERY = "reranker.query"
    """
    Query string for the reranker
    """
    RERANKER_MODEL_NAME = "reranker.model_name"
    """
    Model name of the reranker
    """
    RERANKER_TOP_K = "reranker.top_k"
    """
    Top K parameter of the reranker
    """


class EmbeddingAttributes:
    """
    Attributes for an embedding
    """

    EMBEDDING_TEXT = "embedding.text"
    """
    The text represented by the embedding.
    """
    EMBEDDING_VECTOR = "embedding.vector"
    """
    The embedding vector.
    """


class ToolCallAttributes:
    """
    Attributes for a tool call
    """

    TOOL_CALL_FUNCTION_NAME = "tool_call.function.name"
    """
    The name of function that is being called during a tool call.
    """
    TOOL_CALL_FUNCTION_ARGUMENTS_JSON = "tool_call.function.arguments"
    """
    The JSON string representing the arguments passed to the function
    during a tool call.
    """


class OpenInferenceSpanKindValues(Enum):
    TOOL = "TOOL"
    CHAIN = "CHAIN"
    LLM = "LLM"
    RETRIEVER = "RETRIEVER"
    EMBEDDING = "EMBEDDING"
    AGENT = "AGENT"
    RERANKER = "RERANKER"
    UNKNOWN = "UNKNOWN"
    GUARDRAIL = "GUARDRAIL"
    EVALUATOR = "EVALUATOR"


class OpenInferenceMimeTypeValues(Enum):
    TEXT = "text/plain"
    JSON = "application/json"