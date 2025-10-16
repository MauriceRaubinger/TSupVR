using UnityEngine;
using UnityEngine.AI;
using i5.VirtualAgents;
using System.Diagnostics; // Assuming this is required for your VirtualAgents setup

public class AgentMovement : MonoBehaviour
{
    private NavMeshAgent navAgent;
    public float followDistance = 2f; // Distance to maintain and stop within
    public float catchUpDistance = 5f; // Larger radius to start catching up (hysteresis to prevent jitter)
    public float updateThreshold = 0.5f; // Threshold for updating destination while pursuing (optimizes performance)

    void Start()
    {
        navAgent = GetComponent<NavMeshAgent>();
        if (navAgent == null || !navAgent.enabled)
        {
            UnityEngine.Debug.LogError("NavMeshAgent is missing or disabled.");
            return;
        }

        // Set the stopping distance to maintain space
        navAgent.stoppingDistance = followDistance;

        // Snap agent to the nearest NavMesh position
        if (NavMesh.SamplePosition(transform.position, out NavMeshHit hit, 100f, NavMesh.AllAreas))
        {
            navAgent.Warp(hit.position);
            UnityEngine.Debug.Log("Agent snapped to NavMesh at: " + hit.position);
        }
        else
        {
            UnityEngine.Debug.LogError("No valid NavMesh found near agent position: " + transform.position);
            return;
        }

        // Initial destination setup
        UpdateDestination();
    }

    void Update()
    {
        // Continuously evaluate pursuit
        UpdateDestination();
    }

    private void UpdateDestination()
    {
        if (Camera.main == null)
        {
            UnityEngine.Debug.LogError("No main camera found to follow.");
            return;
        }

        Vector3 cameraPos = Camera.main.transform.position;

        // Sample nearest valid NavMesh point near the camera
        if (NavMesh.SamplePosition(cameraPos, out NavMeshHit targetHit, 100f, NavMesh.AllAreas))
        {
            Vector3 targetPos = targetHit.position;
            float distToTarget = Vector3.Distance(transform.position, targetPos);
            // Start or continue pursuit with hysteresis
            if (distToTarget > catchUpDistance)
            {
                // Update destination only if the target has moved significantly
                if (Vector3.Distance(navAgent.destination, targetPos) > updateThreshold && navAgent.isOnNavMesh)
                {
                    navAgent.SetDestination(targetPos-(targetPos-transform.position).normalized*followDistance);
                    // Debug.Log("Agent pursuing camera to: " + targetPos);
                }
            }
        }
        else
        {
            UnityEngine.Debug.LogWarning("Camera is not near a valid NavMesh: " + cameraPos);
        }
    }
}