using System;
using System.Runtime.InteropServices;
using System.Threading;

class KeySimulator {
    [DllImport("user32.dll")]
    static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);

    const byte VK_CONTROL = 0x11;
    const byte VK_C = 0x43;
    const byte VK_V = 0x56;
    const uint KEYEVENTF_KEYUP = 0x0002;

    static void Main(string[] args) {
        if (args.Length == 0) return;
        string action = args[0].ToLower();
        
        Thread.Sleep(150); // Small delay to let system focus settle

        if (action == "copy") {
            // Press Ctrl
            keybd_event(VK_CONTROL, 0, 0, UIntPtr.Zero);
            // Press C
            keybd_event(VK_C, 0, 0, UIntPtr.Zero);
            Thread.Sleep(50);
            // Release C
            keybd_event(VK_C, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            // Release Ctrl
            keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
        } else if (action == "paste") {
            // Press Ctrl
            keybd_event(VK_CONTROL, 0, 0, UIntPtr.Zero);
            // Press V
            keybd_event(VK_V, 0, 0, UIntPtr.Zero);
            Thread.Sleep(50);
            // Release V
            keybd_event(VK_V, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            // Release Ctrl
            keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
        }
    }
}
