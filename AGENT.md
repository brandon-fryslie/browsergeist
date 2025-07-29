Follow the main loop repeatedly until there is no more work to be completed.

# Main loop

- Reread PROJECT.md to understand the requirements for the project
- Review BACKLOG.md, update as needed to align with PROJECT.md, choose the most important BACKLOG item
- Review TODO.md, updating as needed for alignment
- Implement TODO item
- Update COMPLETED.md and PROGRESS.md as needed
- After completing a TODO item, choose the next TODO item until list is completed
- Review code for refactoring opportunities.
  - Prioritize simplicity, logical and useful abstractions, code reuse, best practices and good code hygiene, modularity, robust error handling
  - Add missing tests
  - Ensure code is functional by retesting after changes

# Document Requirements

- Agent must pay attention to the following significant files.  The contents are as described for each file.  Agent will auto reread the file as described in 'Read when'.  The agent will auto update the file as described in 'Updated when'. Read/update only as described or when asked to.
  - AGENT.md is updated with new Agent instructions / rules when they lead to success
    - Contents: Rules to guide agent
    - Read when: When agent needs instructions
    - Updated when: Asked
  - PROJECT.md 
    - Contents: High level document explaining the projects goals, features, requirements, etc.
    - Read when: Agent needs to understand the project
    - Updated when: Planning new features or elaboration of existing features for the project
  - PROGRESS.md 
    - Contents: A document describing the current status of the project implementation.  Serves as an overall log of progress and acomplishments.
    - Read when: Agent needs to know what has been implemented and what has not
    - Updated when: We update PROJECT.md, or we finish work.  PROGRESS.md must aways be kept in an accurate state
  - BACKLOG.md 
    - Contents: The work that has been broken down into stories, but not read to pull immediately.
    - Read when: When want understand overall plan.  When all TODO items are completed and need to break down more work.
    - Updated when: to remove work that has been completed (move to COMPLETED.md, update PROGRESS.md)
  - TODO.md 
    - Contents: The current work that is in progress or planned for the immediate future
    - Read when: Agent needs to review the plan, or needs to find a new task to work on
    - Updated when: We complete work and need to find new work, or we update PROJECT.md or BACKLOG.md and need to ensure the plans are aligned
    - is updated to reflect the top priority in BACKLOG.md, as well as when tasks are completed and moved to COMPLETED.md
  - COMPLETED.md - the completed features/tasks
    - Contents: List of completed work
    - Read when: Asked
- If any of these files do not exist, create them

# Testing Requirements

- All code must be thoroughly tested with meaningful tests
- Tests should be useful and test specific functionality in a non-trivial way
- Mocks should not make tests tautologically true - test real behavior
- Testability should guide abstractions and implementation design
- Tests should be written at appropriate layers to improve future implementation and refactoring
- Integration tests should test real component interactions
- Unit tests should test individual component behavior with minimal mocking
- Use pytest for Python testing with proper fixtures and parameterization
- Tests must be added for all new functionality before completion
- See TESTING.md for how to run tests and overview of test architecture

⸻

# Python Environment Rules

- Always use `uv` virtual environments for Python package management
- Always use `python3` command explicitly when calling Python (never just `python`)
- Activate virtual environment with `source .venv/bin/activate` before running Python scripts
- Use `uv` for installing and managing Python dependencies

⸻

# CAPTCHA System Implementation

- Successfully implemented comprehensive CAPTCHA solving with 3 methods:
  - OpenAI API integration for automated solving using GPT-4 Vision
  - Manual webserver for user-assisted solving via Flask interface
  - 2Captcha service integration for outsourced solving
- CAPTCHA detection uses multi-modal approach: template matching, OCR, pattern recognition
- Seamlessly integrated with HumanMouse automation framework
- Provides automatic CAPTCHA handling during automation workflows
- Includes robust error handling and intelligent fallback mechanisms
- Production-ready with comprehensive examples and documentation

⸻

# Simulated Functionality Rule

- Simulated or placeholder functionality may be temporarily used to structure programs and examples during development
- However, work is NOT considered complete until ALL simulated functionality is replaced with actual working implementations
- Comments like "Simulated xyz", "Placeholder for xyz", or "TODO: implement xyz" indicate incomplete work
- When the project is production-ready, there will be NO simulated functionality - everything must be fully functional
- This rule applies to all code: examples, core functionality, tests, and documentation

⸻

# Code Quality Rules

- Always fix all compiler warnings before completing tasks
- Use `@unchecked Sendable` for thread-safe classes with internal synchronization
- Replace unused variables with `_` in Swift (e.g., `for (_, item)` instead of `for (index, item)`)
- Use `!= nil` instead of capturing unused guard variables
- Make classes `final` when inheritance is not needed to improve performance

⸻

