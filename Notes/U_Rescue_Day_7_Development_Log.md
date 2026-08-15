# U-Rescue Day 7 Development Log

Date: 2026-08-16

## Summary
Today’s work focused on cleaning up the project repository and stabilizing the GitHub state. The main objective was to remove accidental large files and generated artifacts from Git tracking so the project can remain lightweight and shareable.

## Key updates
- Verified the correct GitHub repository connection.
- Identified the root cause of the repeated push failures: large tracked files, especially the training dataset and model output CSVs.
- Added and refined the repository ignore rules to prevent `.venv`, `node_modules`, dataset folders, model folders, and generated files from being pushed again.
- Cleaned the tracked Git history to remove oversized project artifacts.
- Prepared a clean project baseline for future collaboration and deployment.

## Repository hygiene decisions
- Keep source code and documentation in Git.
- Exclude generated model files, environment folders, and dataset artifacts.
- Store only essential project files and code logic in the repository.
- Keep raw GIS and training datasets outside Git unless they are deliberately managed with Git LFS.

## Next actions
1. Continue refining the backend and core ML logic.
2. Keep the frontend source clean and remove any generated build artifacts.
3. Validate the project runs locally without dependency issues.
4. Maintain the repo with small, focused commits instead of uploading large generated outputs.

## Notes
This repository is now in a much cleaner state for future GitHub work. The emphasis is on keeping only meaningful project files, while excluding environment and large output artifacts that do not belong in a code repository.
