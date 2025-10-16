using System.Diagnostics;
using UnityEngine;
using UnityEngine.AI;

public class PlayerNavCheck : MonoBehaviour
{
    public float speed = 5f; 
    public float meshQueryDistance = 0.5f; 
    private CharacterController controller;
    private NavMeshHit hit;

    void Start()
    {
        controller = GetComponent<CharacterController>();
        if (controller == null)
        {
            UnityEngine.Debug.LogError("No CharacterController");
            enabled = false;
        }
    }

    void Update()
    {
        Vector3 inputDirection = new Vector3(Input.GetAxis("Horizontal"), 0f, Input.GetAxis("Vertical"));
        inputDirection = transform.TransformDirection(inputDirection.normalized);

        if (inputDirection.magnitude > 0f)
        {
            Vector3 targetPosition = transform.position + inputDirection * speed * Time.deltaTime;
            if (NavMesh.SamplePosition(targetPosition, out hit, meshQueryDistance, NavMesh.AllAreas))
            {
                controller.Move(inputDirection * speed * Time.deltaTime);
            }
            else
            {
                if (NavMesh.SamplePosition(transform.position, out hit, meshQueryDistance * 2f, NavMesh.AllAreas))
                {
                    Vector3 safeDirection = (hit.position - transform.position).normalized;
                    controller.Move(safeDirection * speed * Time.deltaTime * 0.5f);
                    UnityEngine.Debug.Log("Teetering on the brink—realigning.");
                }
                else
                {
                    UnityEngine.Debug.LogWarning("Void claims all. Re-forge the NavMesh.");
                }
            }
        }
    }

    void LateUpdate()
    {
        if (!NavMesh.SamplePosition(transform.position, out hit, meshQueryDistance, NavMesh.AllAreas))
        {
            if (NavMesh.SamplePosition(transform.position, out hit, Mathf.Infinity, NavMesh.AllAreas))
            {
                transform.position = hit.position; 
                UnityEngine.Debug.Log("Off the grid—returned to the path's embrace.");
            }
            else
            {
                UnityEngine.Debug.LogError("No haven in sight. The mesh is shattered—rebuild.");
            }
        }
    }
}
