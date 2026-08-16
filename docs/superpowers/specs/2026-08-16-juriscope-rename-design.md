# Juriscope Rename Design

## Goal

Rename the LegalRAG application to **Juriscope** across public-facing project materials.

## Scope

- Change the name displayed in the web application to Juriscope.
- Change the FastAPI title and health-check message to Juriscope.
- Update the README, startup banner, project helper copy, presentation source text, and chatbot farewell message.

## Compatibility

- Preserve the existing Pinecone index identifier (`legal-rag`) and all API routes, environment-variable names, and code module paths. These are operational identifiers rather than user-facing branding.
- Keep the workspace directory name unchanged; renaming it would require updating local paths and could disrupt the current setup.

## Validation

- Search the tracked source and documentation for remaining user-facing `LegalRAG` references.
- Run the frontend lint command and backend test suite where available.
