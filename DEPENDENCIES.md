# Dependencies for AURA Research Assistant

The following dependencies are required for running this application on Render or any other hosting platform:

```
flask==2.3.3
flask-sqlalchemy==3.1.1
gunicorn==23.0.0
numpy==1.26.4
openai==1.12.0
scikit-learn==1.4.1
sqlalchemy==2.0.28
tensorflow==2.15.0
```

## Environment Variables

The following environment variables must be set in the Render dashboard or hosting platform:

- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: Database connection URL (if using a hosted database)
- `SESSION_SECRET`: Random string for session security

## Notes for Deployment

- The application listens on port 5000 by default
- Use Gunicorn with the command: `gunicorn --bind 0.0.0.0:$PORT --reuse-port main:app`
- For Render, the `PORT` environment variable is automatically provided
- TensorFlow warnings about CUDA can be safely ignored as they do not affect functionality