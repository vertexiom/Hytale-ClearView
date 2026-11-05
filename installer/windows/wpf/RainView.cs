/*
 * Copyright (C) 2026 vertexiom
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * This file is part of Hytale ClearView.
 * Hytale ClearView is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version. See LICENSE for details.
 */
using System.Diagnostics;
using System.Globalization;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;

namespace ClearView.Setup;
public sealed class RainView : FrameworkElement
{
    private static readonly string[] Banner = ["  ___ _               __   ___            ", @" / __| |___ __ _ _ _  \ \ / (_)_____ __ __", @"| (__| / -_) _` | '_|  \ V /| / -_) V  V /", @" \___|_\___\__,_|_|     \_/ |_\___|\_/\_/ "];
    private sealed class RainDrop { public double X, Y, Speed, Depth; public bool Collides; }
    private sealed class Splash { public double X, Y, Vx, Vy = -30, Life = .45; }
    private readonly Random random = new();
    private readonly List<RainDrop> drops = [];
    private readonly List<Splash> splashes = [];
    private readonly Dictionary<(string, double, string, double), BitmapSource> glyphs = [];
    private readonly Stopwatch clock = Stopwatch.StartNew();
    private double last, emission;
    private Size field;
    private bool listening;
    public bool Paused { get; set; }
    public bool Suspended { get; set; }
    public RainView()
    {
        Loaded += (_, _) => { if (!listening) { CompositionTarget.Rendering += Frame; listening = true; last = clock.Elapsed.TotalSeconds; } };
        Unloaded += (_, _) => Stop();
    }
    public void Stop() { if (listening) CompositionTarget.Rendering -= Frame; listening = false; }
    private static SolidColorBrush Brush(string hex) { var b = (SolidColorBrush)new BrushConverter().ConvertFromString(hex)!; b.Freeze(); return b; }
    private static readonly Brush BackgroundBrush = Brush("#071018");
    private void Write(DrawingContext dc, string text, double x, double y, double size, string color)
    {
        double dpi = VisualTreeHelper.GetDpi(this).PixelsPerDip;
        var key = (text, size, color, dpi);
        if (!glyphs.TryGetValue(key, out var bitmap))
        {
            if (glyphs.Count > 600) glyphs.Clear();
            var formatted = new FormattedText(text, CultureInfo.InvariantCulture, FlowDirection.LeftToRight,
                new Typeface(new FontFamily(new Uri("pack://application:,,,/"), "./Fonts/#JetBrains Mono"), FontStyles.Normal, FontWeights.Bold, FontStretches.Normal), size, Brush(color), dpi);
            var visual = new DrawingVisual();
            using (var context = visual.RenderOpen()) context.DrawText(formatted, new Point(2, 2));
            var raster = new RenderTargetBitmap(Math.Max(1,(int)Math.Ceiling((formatted.WidthIncludingTrailingWhitespace+6)*dpi)),
                Math.Max(1,(int)Math.Ceiling((formatted.Height+6)*dpi)), 96*dpi,96*dpi,PixelFormats.Pbgra32);
            raster.Render(visual); raster.Freeze(); bitmap=raster; glyphs[key]=bitmap;
        }
        dc.DrawImage(bitmap, new Rect(x-2,y-2,bitmap.Width,bitmap.Height));
    }

    private IEnumerable<(double X, double Y, char C)> Cells()
    {
        double cw = (ActualWidth-28)/43, ch = cw*1.95, floor = ActualHeight-80;
        double top = (68+floor-Banner.Length*ch)/2;
        for (int y=0;y<Banner.Length;y++) for (int x=0;x<Banner[y].Length;x++) if (Banner[y][x]!=' ') yield return (14+x*cw, top+y*ch, Banner[y][x]);
    }
    private RainDrop NewDrop(double x, double y)
    {
        double depth = .65+random.NextDouble()*.6;
        return new RainDrop { X=x, Y=y, Speed=110*depth, Depth=depth, Collides=random.NextDouble()<.45 };
    }
    private void Fill()
    {
        if (RenderSize==field || ActualWidth<30 || ActualHeight<160) return;
        field=RenderSize; drops.Clear(); splashes.Clear(); emission=0; glyphs.Clear();
        int columns=Math.Max(1,(int)((ActualWidth-24)/14)), rows=Math.Max(1,(int)((ActualHeight-140)/19));
        for (int y=0;y<rows && drops.Count<1800;y++) for (int x=0;x<columns && drops.Count<1800;x++) drops.Add(NewDrop(12+(x+random.NextDouble())*(ActualWidth-24)/columns,60+(y+random.NextDouble())*(ActualHeight-140)/rows));
    }
    private void Frame(object? sender, EventArgs e)
    {
        double now=clock.Elapsed.TotalSeconds, dt=Math.Min(now-last,.25); last=now;
        if (Paused || Suspended || !IsVisible || !SystemParameters.ClientAreaAnimation) return;
        Fill(); double w=ActualWidth, floor=ActualHeight-80;
        if (w<30 || floor<60) return;
        double width=w-24, height=floor-60, side=.24*height;
        emission+=dt*90*(width+side)/276;
        while(emission>=1)
        {
            emission--;
            if(drops.Count>=1800) continue;
            bool top=random.NextDouble()<width/(width+side);
            drops.Add(NewDrop(top ? 12+random.NextDouble()*width : 12,top ? 60 : 60+random.NextDouble()*height));
        }
        var cells=Cells().ToArray(); double cw=(w-28)/43, ch=cw*1.95;
        for(int i=drops.Count-1;i>=0;i--)
        {
            var d=drops[i]; double old=d.Y; d.X+=d.Speed*.24*dt; d.Y+=d.Speed*dt;
            double? hit=d.Y>=floor ? floor : null;
            if(hit==null && d.Collides) foreach(var cell in cells) if(cell.X-cw*.45<=d.X && d.X<cell.X+cw && old<=cell.Y+ch*.4 && d.Y>=cell.Y) { hit=cell.Y; break; }
            if(hit!=null) foreach(int sign in new[]{-1,1}) splashes.Add(new Splash { X=d.X, Y=hit.Value, Vx=sign*(12+random.NextDouble()*16) });
            if(hit!=null || d.X>=w-12) drops.RemoveAt(i);
        }
        foreach(var p in splashes) { p.Life-=dt; p.X+=p.Vx*dt; p.Y+=p.Vy*dt; p.Vy+=150*dt; }
        splashes.RemoveAll(p=>p.Life<=0); if(splashes.Count>200) splashes.RemoveRange(0,splashes.Count-200);
        InvalidateVisual();
    }
    protected override void OnRender(DrawingContext dc)
    {
        base.OnRender(dc); dc.DrawRectangle(BackgroundBrush,null,new Rect(RenderSize)); Fill();
        double cw=(ActualWidth-28)/43, floor=ActualHeight-80;
        if(cw<=0 || floor<60) return;
        dc.PushClip(new RectangleGeometry(new Rect(12,60,ActualWidth-24,floor-60)));
        foreach(var d in drops) { dc.PushOpacity(.25+d.Depth*.35); Write(dc,"\\",d.X,d.Y,cw*1.65,"#78B5D9"); dc.Pop(); }
        dc.Pop();
        foreach(var c in Cells()) Write(dc,c.C.ToString(),c.X,c.Y,cw*1.65,"#D1EDFA");
        for(double x=12;x<ActualWidth-12;x+=Math.Max(1,Math.Round(cw))) Write(dc,"_",x,floor,cw*1.65,"#527D94");
        foreach(var p in splashes) { dc.PushOpacity(Math.Max(0,p.Life/.45)); Write(dc,p.Life>.3 ? "'" : ".",p.X,p.Y,cw*1.65,"#A8D9F0"); dc.Pop(); }
        Write(dc,"CLEARVIEW / VERTEXIOM",25,25,11,"#8CA6B8");
        Write(dc,"v0.1.3 · em desenvolvimento",25,ActualHeight-35,11,"#8CA6B8");
    }
}
