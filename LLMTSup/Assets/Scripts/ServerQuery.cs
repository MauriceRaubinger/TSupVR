using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Text;
using System.Threading.Tasks;
using System;
using System.Net;
using System.Net.Sockets;
using System.Diagnostics;

public class PythonCaller : MonoBehaviour
{
    [SerializeField] public string promptInjection = "";
    public string serverUrl = "http://192.168.0.225:5000/run"; // Default fallback
    public TooltipTextSetter tt;
    private bool serverDiscovered = false;

    async void Start()
    {
        await DiscoverServerAsync();
        // Example usage after discovery:
        // string ans = await GetAnswerAsync("Test");
        // tt.SetTooltipText(ans);
    }

    public async Task DiscoverServerAsync()
    {
        const int discoveryPort = 5001;
        const string discoveryMessage = "FLASK_DISCOVERY";
        const int timeoutMs = 2000; // 2 seconds timeout

        using (UdpClient udpClient = new UdpClient())
        {
            udpClient.EnableBroadcast = true;

            // Send broadcast
            byte[] sendBytes = Encoding.ASCII.GetBytes(discoveryMessage);
            await udpClient.SendAsync(sendBytes, sendBytes.Length,
                new IPEndPoint(IPAddress.Broadcast, discoveryPort));

            // Listen for response with timeout
            var receiveTask = udpClient.ReceiveAsync();
            var timeoutTask = Task.Delay(timeoutMs);
            var completedTask = await Task.WhenAny(receiveTask, timeoutTask);

            if (completedTask == receiveTask)
            {
                UdpReceiveResult result = await receiveTask;
                string response = Encoding.ASCII.GetString(result.Buffer);
                UnityEngine.Debug.Log("Received: " + response);

                if (response.StartsWith("FLASK_SERVER:"))
                {
                    string[] parts = response.Split(':');
                    if (parts.Length >= 3)
                    {
                        serverUrl = $"http://{parts[1]}:{parts[2]}/run";
                        serverDiscovered = true;
                        UnityEngine.Debug.Log($"Discovered server at: {serverUrl}");
                    }
                }
            }
            else
            {
                UnityEngine.Debug.LogWarning("Server discovery timed out. Using default URL.");
            }
        }
    }

    public IEnumerator SendQuestion(string question)
    {
        string jsonData = JsonUtility.ToJson(new QuestionData { question = question + promptInjection });
        byte[] postData = Encoding.UTF8.GetBytes(jsonData);
        UnityWebRequest request = new UnityWebRequest(serverUrl, "POST");
        request.uploadHandler = new UploadHandlerRaw(postData);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            string rawResponse = request.downloadHandler.text;
            string cleanText = ProcessJsonResponse(rawResponse);

            UnityEngine.Debug.Log("Raw response: " + rawResponse);
            UnityEngine.Debug.Log("Clean answer: " + cleanText);
            UnityEngine.Debug.Log(promptInjection);
        }
        else
        {
            UnityEngine.Debug.LogError("Error: " + request.error);
        }
    }

    // New async method for awaitable results
    public async Task<string> GetAnswerAsync(string question)
    {
        string jsonData = JsonUtility.ToJson(new QuestionData { question = question + promptInjection});
        byte[] postData = Encoding.UTF8.GetBytes(jsonData);
        UnityEngine.Debug.Log(promptInjection);
        using (UnityWebRequest request = new UnityWebRequest(serverUrl, "POST"))
        {
            request.uploadHandler = new UploadHandlerRaw(postData);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            var asyncOp = request.SendWebRequest();
            while (!asyncOp.isDone)
            {
                await Task.Yield();  // Non-blocking wait
            }

            if (request.result == UnityWebRequest.Result.Success)
            {
                string rawResponse = request.downloadHandler.text;
                string cleanText = ProcessJsonResponse(rawResponse);

                UnityEngine.Debug.Log("Raw response: " + rawResponse);
                UnityEngine.Debug.Log("Clean answer: " + cleanText);

                return cleanText;  // Return the cleaned text instead of raw JSON
            }
            else
            {
                throw new System.Exception("Error: " + request.error);
            }
        }
    }

    // Method to process the JSON response and extract clean text
    private string ProcessJsonResponse(string jsonString)
    {
        try
        {
            // Parse the JSON response
            ApiResponse response = JsonUtility.FromJson<ApiResponse>(jsonString);

            if (response != null && !string.IsNullOrEmpty(response.result))
            {
                // Clean up the escaped characters
                return CleanupText(response.result);
            }
            else
            {
                UnityEngine.Debug.LogWarning("Empty or invalid response");
                return "No response received";
            }
        }
        catch (System.Exception e)
        {
            UnityEngine.Debug.LogError("Error parsing JSON response: " + e.Message);
            return "Error processing response";
        }
    }

    // Method to clean up escaped characters in the text
    private string CleanupText(string rawText)
    {
        if (string.IsNullOrEmpty(rawText))
            return rawText;

        // Replace escaped newlines with actual newlines
        string cleaned = rawText.Replace("\\n", "\n");

        // Replace escaped quotes
        cleaned = cleaned.Replace("\\\"", "\"");

        // Replace escaped backslashes
        cleaned = cleaned.Replace("\\\\", "\\");

        // Replace escaped tabs if any
        cleaned = cleaned.Replace("\\t", "\t");

        return cleaned;
    }

    [System.Serializable]
    public class QuestionData
    {
        public string question;
    }

    [System.Serializable]
    public class ApiResponse
    {
        public string result;
    }
}