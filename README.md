## Overview

This project's VR-Frontend was designed for the **Meta Quest 3**. To easily run the specification used in the bachelor thesis, the **`.apk`** file must be transferred to an MQ3. The Backend component can be set up on a local computer.

## Demo Video

[View an example video of the application in action.](https://drive.google.com/file/d/1uqTLzUAn7ajoz-idCTF46O_Q0awQBOPR/view?usp=sharing)

---

## Prerequisites

* **Unity Hub** with a compatible Unity version (see project details).
* PC or Laptop with **Python 3.8+**.
* A **Meta Quest 3** headset with developer mode enabled.
* API keys for **Google Gemini**, **LangChain**, and **Wit.ai**.

---

## Setup

### VR Front-End (Meta Quest 3)

1.  Open the Unity project located in the repository.
2.  Install any required packages prompted by Unity.
3.  Configure the project for Android (Oculus) builds.
4.  Build and deploy the application to your Meta Quest 3.

### Backend Server (Local Computer)

1.  Install the required Python packages.
2.  Add your API keys to the configuration.
3.  Run the server: `llmserverhost.py`.

---

## For End-Users (Usage)

1.  Put on the VR headset and launch the application.
2.  Interact with the Virtual Agent by looking at it and speaking.
3.  Point at or interact with waypoints on the 3D model to ask contextual questions.
4.  Use voice commands (as defined in the workflow graph) to manipulate the environment (e.g., "Lift the engine.").

---

## For Authors/Developers (Configuration)

1.  **Load a 3D Model**: Import your 3D model into the Unity environment and set the waypoint prefabs across its components.
2.  **Prepare Documentation**: Write your documentation in the `Machine_Docs.txt` files with the technical information for your model.
3.  **Create a Workflow Graph**: Use the LLM Graph Creator to design the agent's logic. Define how it should classify user intent, when to retrieve from documentation, and how to handle commands. Save the graph as a JSON file.
4.  **Run**: Load the JSON graph in the Flask server and start the VR application.

---

## Acknowledgements

Open-source 3D models were taken from [www.sketchfab.com](https://www.sketchfab.com) by the following creators:

* [ahmagh2e](https://sketchfab.com/ahmagh2e)
* [davidgulla](https://sketchfab.com/davidgulla)
* [veebroush](https://sketchfab.com/veebroush)
* [mark-peters](https://sketchfab.com/mark-peters)
* [Cyril43](https://sketchfab.com/Cyril43)
