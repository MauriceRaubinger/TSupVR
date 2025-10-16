using UnityEngine;
using System.Collections.Generic; // Required for using Lists

public class ObjectRestorer : MonoBehaviour
{
    private class TransformState
    {
        public Transform Transform;
        public Vector3 Position;
        public Quaternion Rotation;
    }   
    private List<TransformState> initialStates;
    void Awake()
    {
        initialStates = new List<TransformState>();
        Transform[] allTransforms = GetComponentsInChildren<Transform>(true);
        foreach (Transform trans in allTransforms)
        {
            initialStates.Add(new TransformState
            {
                Transform = trans,
                Position = trans.position,
                Rotation = trans.rotation
            });
        }
    }

    public void ResetObjectState()
    {
        foreach (var state in initialStates)
        {
            if (state.Transform != null)
            {
                state.Transform.position = state.Position;
                state.Transform.rotation = state.Rotation;
            }
        }
    }
}