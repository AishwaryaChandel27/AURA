# AURA API Documentation

This document describes the API endpoints provided by the AURA Research Assistant.

## Base URL

All API endpoints are relative to the base URL of your AURA installation:

```
http://localhost:5000/api
```

## Authentication

Currently, AURA does not implement authentication for API endpoints. This may change in future versions.

## API Health Check

### GET /api/health

Check if the API is available and determine which services are functioning.

**Example Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-03-30T12:34:56Z",
  "tensorflow_available": true,
  "openai_available": true
}
```

## Paper Analysis

### POST /api/analyze

Analyze a collection of research papers using TensorFlow.

**Request Body:**
```json
{
  "papers": [
    {
      "id": "paper_id_1",
      "title": "Paper Title 1",
      "abstract": "Paper abstract text...",
      "authors": ["Author 1", "Author 2"],
      "published_date": "2023-05-15",
      "source": "arxiv",
      "external_id": "2304.12345"
    },
    {
      "id": "paper_id_2",
      "title": "Paper Title 2",
      "abstract": "Second paper abstract text...",
      "authors": ["Author 3", "Author 4"],
      "published_date": "2024-01-10",
      "source": "semantic_scholar",
      "external_id": "12345678"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "topics": [
    {
      "name": "Deep Learning",
      "weight": 0.85
    },
    {
      "name": "Computer Vision",
      "weight": 0.72
    }
  ],
  "trends": [
    {
      "name": "Transformer Architecture",
      "growth": 0.65,
      "year": 2022
    }
  ],
  "clusters": [
    {
      "id": 0,
      "label": "Neural Networks",
      "papers": ["paper_id_1"]
    },
    {
      "id": 1,
      "label": "Image Recognition",
      "papers": ["paper_id_2"]
    }
  ]
}
```

## Text Analysis

### POST /api/analyze/text

Analyze text using TensorFlow for topic classification or sentiment analysis.

**Request Body:**
```json
{
  "text": "The impact of deep learning architectures on computer vision has been profound, particularly in object detection and segmentation.",
  "analysis_type": "topic"
}
```

**Response (Topic Classification):**
```json
{
  "success": true,
  "topic": "Computer Science",
  "confidence": 0.92,
  "all_topics": {
    "Computer Science": 0.92,
    "Artificial Intelligence": 0.85,
    "Machine Learning": 0.78
  }
}
```

**Sentiment Analysis Request:**
```json
{
  "text": "The recent advancements in AI have been remarkable, leading to significant improvements in efficiency and accuracy.",
  "analysis_type": "sentiment"
}
```

**Response (Sentiment Analysis):**
```json
{
  "success": true,
  "sentiment": "positive",
  "score": 0.87
}
```

## Text Generation

### POST /api/generate

Generate text using the OpenAI API. Requires a valid OpenAI API key to be configured.

**Request Body:**
```json
{
  "prompt": "Explain the concept of attention mechanisms in transformer models",
  "max_tokens": 250
}
```

**Response:**
```json
{
  "success": true,
  "text": "Attention mechanisms in transformer models allow the model to focus on different parts of the input sequence when generating each part of the output. Unlike traditional sequence models that process data sequentially, transformers process the entire sequence at once, using attention to determine which elements are most relevant to each other..."
}
```

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Endpoint not found
- `500 Internal Server Error`: Server-side error

Error responses include a JSON body with an error message:

```json
{
  "error": "Error message details"
}
```

## Rate Limiting

Currently, AURA does not implement rate limiting for API endpoints. This may change in future versions.

## API Versioning

The API does not currently use explicit versioning. Future breaking changes will be announced in advance.

## Deprecation Policy

APIs may be deprecated over time. Deprecated endpoints will continue to function for at least 6 months after deprecation notice, with warnings provided in responses.