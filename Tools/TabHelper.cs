
using System;
using UnityEngine;
using System.Reflection;

namespace Table
{
    public static class TabHelper
    {
        public static string TablePath = Application.dataPath + "/Resources/Table/{0}.dat";

        public static void InitTables()
        {
            var properties = typeof(TabMgr).GetProperties(BindingFlags.Static | BindingFlags.Public | BindingFlags.Instance);
            for (int i = 0; i < properties.Length; i++)
            {
                object t = properties[i].GetValue(null);
                t.GetType().InvokeMember("LoadFile", BindingFlags.Public | BindingFlags.InvokeMethod | BindingFlags.Instance, null, t, null);
            }
        }
    }

}
