// Copyright (C) 2026 vertexiom
// SPDX-License-Identifier: GPL-3.0-or-later
using System.Windows;
using System.Windows.Input;

namespace ClearView.Setup;

// Track input modality independently of Wine's remembered keyboard focus state.
public static class FocusCue
{
    public static readonly DependencyProperty KeyboardNavigationProperty = DependencyProperty.RegisterAttached(
        "KeyboardNavigation", typeof(bool), typeof(FocusCue),
        new FrameworkPropertyMetadata(false, FrameworkPropertyMetadataOptions.Inherits));
    public static bool GetKeyboardNavigation(DependencyObject target) => (bool)target.GetValue(KeyboardNavigationProperty);
    public static void SetKeyboardNavigation(DependencyObject target, bool value) => target.SetValue(KeyboardNavigationProperty, value);
    private static bool initialized;
    public static void Initialize()
    {
        if (initialized) return;
        initialized = true;
        EventManager.RegisterClassHandler(typeof(Window), Keyboard.PreviewKeyDownEvent,
            new KeyEventHandler((sender, e) => { if (e.Key == Key.Tab) SetKeyboardNavigation((DependencyObject)sender, true); }), true);
        EventManager.RegisterClassHandler(typeof(Window), Mouse.PreviewMouseDownEvent,
            new MouseButtonEventHandler((sender, _) => SetKeyboardNavigation((DependencyObject)sender, false)), true);
        EventManager.RegisterClassHandler(typeof(Window), UIElement.PreviewTouchDownEvent,
            new EventHandler<TouchEventArgs>((sender, _) => SetKeyboardNavigation((DependencyObject)sender!, false)), true);
    }
}
