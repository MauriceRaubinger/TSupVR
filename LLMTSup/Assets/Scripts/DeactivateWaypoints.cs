using UnityEngine;

public class ObjectDeactivator : MonoBehaviour
{
    public void DeactivateObject()
    {
        gameObject.SetActive(false);
    }
}
