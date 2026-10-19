# Definitions of Done - Urbanex
- The next criteria, its what we use to evaluate and test if every HU (User History) is enough to be functional, and retrieve to the user, the bussiness value what we want actually.
- Tests made with Postmant.

*Translation to Spanish [Español](DefinitionOfDone.es.md)*

## Backend Criteria (Black Box Testing)
- [ ] Strict Authentication: All write paths (POST, PUT, PATCH, DELETE) require a valid JWT token. Requests without a token return `401 Unauthorized`.
- [ ] Role-Based Authorization: The system validates that the user is the owner or administrator of the resource. Violations return `403 Forbidden`.
- [ ] Payload Integrity: Requests with empty required fields or incorrect data types are rejected with `400 Bad Request`.
- [ ] Public Availability: Query endpoints (GET) intended for the end client, such as the property catalog, respond with `200 OK` without requiring authentication.

## Frontend Criteria(MVP Funcional)
- [ ] Navigability: The user can access the flow from the main interface without blocking or 404 errors.
- [ ] API Consumption: The frontend communicates correctly with the backend, securely managing tokens in the headers.
- [ ] Visual Feedback: The interface reacts to the success or failure of an operation (e.g., the newly published property appears immediately in the grid).
- [ ] Multimedia Handling: External images (such as those served by Django) are allowed and rendered without breaking the design.

---*Note: No functionality is considered complete if it only works in Postman. It must be executable through the graphical interface.*