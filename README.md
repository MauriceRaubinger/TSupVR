Open source 3D models were taken from www.sketchfab.com by the following creators:
https://sketchfab.com/ahmagh2e
https://sketchfab.com/davidgulla
https://sketchfab.com/veebroush
https://sketchfab.com/mark-peters
https://sketchfab.com/Cyril43

The VR-Frontend was designed for the Meta Quest 3. To easily run the specification used in the bachelor thesis the .apk file has to be transferred to a MQ3. The Backend component can be setup with a local computer.


Prerequisites

-Unity Hub with a compatible Unity version (see project details).

-PC or Laptop with Python 3.8+

-A Meta Quest 3 headset with developer mode enabled.

-API keys for Google Gemini and Wit.ai.

Setup the VR Front-End:

-Open the Unity project located in the repository.

-Install any required packages prompted by Unity.

-Configure the project for Android (Oculus) builds.

-Build and deploy the application to your Meta Quest 3.


Setup the Backend Server:

-Install the required Python packages.

-Add your API keys

-Run llmserverhost.py.


For Authors/Developers (Configuration)

-Load a 3D Model: Import your 3D model into the Unity environment.

-Prepare Documentation: Create .txt files with the technical information for your model.

-Create a Workflow Graph: Use the LLM Graph Creator to design the agent's logic. Define how it should classify user   intent, when to retrieve from documentation, and how to handle commands. Save the graph as a JSON file.

-Run: Load the JSON graph in the Flask server and start the VR application.


For End-Users

Put on the VR headset and launch the application.

Interact with the Virtual Agent by looking at it and speaking.

Point at or interact with waypoints on the 3D model to ask contextual questions.

Use voice commands (as defined in the workflow graph) to manipulate the environment, e.g., "Lift the engine."
