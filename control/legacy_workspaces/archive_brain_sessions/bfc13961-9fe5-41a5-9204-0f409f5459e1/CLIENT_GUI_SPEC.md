# Client GUI Specification: "The Retro Robot"

## 1. Overview
A specialized, simplified interface for the end-client. It hides all "engineering" complexity (Terminal, Reactor, Logs) and presents a single interaction point: The Robot.

## 2. Visual Design
### The Hero Image
- **Asset**: `uploaded_media_1769896364339.png` (Retro Blue Robot)
- **Placement**: Centered vertically and horizontally.
- **Sizing**: Responsive, max-width 500px.

### The Input ("Teeth Type")
- **Concept**: The text input field is visually integrated into the robot's mouth.
- **Positioning**: Absolute overlay on the image.
- **Styling**:
    - **Background**: Transparent (or matching mouth color).
    - **Border**: None (or subtle highlight on focus).
    - **Font**: Monospace (Retro terminal style), e.g., `VT323` or `Courier New`.
    - **Color**: White or Green (CRT phosphor style).
    - **Cursor**: Blinking block.

## 3. Implementation Plan
### File: `services/sentinel-core/client_view.html`
A standalone HTML file served by Nginx/Python in the container.

```html
<div class="robot-container">
    <img src="assets/robot_face.png" class="robot-face" />
    <input type="text" class="robot-mouth-input" placeholder="COMMAND..." autofocus />
</div>
```

### CSS Logic
```css
.robot-container {
    position: relative;
    display: inline-block;
}
.robot-mouth-input {
    position: absolute;
    bottom: 22%; /* Adjust based on image */
    left: 25%;   /* Adjust based on image */
    width: 50%;  /* Adjust based on image */
    height: 10%; /* Adjust based on image */
    background: transparent;
    border: none;
    color: #00ff00;
    font-family: 'Courier New', monospace;
    font-size: 1.5rem;
    text-align: center;
    outline: none;
}
```

## 4. Licensing Note
> [!WARNING]
> The source of the provided image is unverified. If this is for commercial distribution, ensure you have the rights to use it. Recommended to replace with a commissioned asset or confirmed CC0 SVG for production.
