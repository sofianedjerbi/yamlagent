# Testing the Sound Effects

## How to Test

1. **Start the application:**
   ```bash
   uv run calc3d
   ```

2. **Open in browser:**
   Navigate to `http://localhost:5000`

3. **Test Sound Effects:**

### Basic Operations
- Click number buttons (0-9) → Should hear A4 note (440 Hz)
- Click operators (+, -, ×, ÷) → Should hear C5 note (523 Hz)
- Click parentheses ( ) → Should hear D5 note (587 Hz)
- Click power buttons (x², x³, √) → Should hear F5 note (698 Hz)

### Special Actions
- Click **C** (Clear) → Should hear descending tone (880→220 Hz)
- Click **⌫** (Delete) → Should hear short G4 beep (392 Hz)
- Click **=** (Equals) with valid expression → Should hear pleasant C-E-G chord
- Click **=** with invalid expression → Should hear dissonant error chord

### Visual Effects
- **Button Press:** Watch for ripple animation expanding from click point
- **Equals Button:** Special pulse animation with glow effect
- **Successful Calculation:** Display shimmers with green color
- **Error:** Display shakes with red color
- **Hover:** Buttons lift up with enhanced shadow

### Sound Toggle
- Click 🔊 icon in top-right of display
  - Icon changes to 🔇
  - All sounds disabled
  - Setting saved to localStorage
- Click 🔇 icon
  - Icon changes back to 🔊
  - Plays success arpeggio to confirm re-enabling
  - Setting persisted

### Keyboard Testing
All keyboard inputs also trigger sound effects:
- Type numbers → Number sounds
- Type operators → Operator sounds
- Press Enter → Equals sound + animation
- Press Escape → Clear sound
- Press Backspace → Delete sound

## Expected Behavior

✅ Sounds should be crisp and pleasant, not harsh
✅ Visual animations should be smooth (no jank)
✅ Sound toggle state should persist after page reload
✅ No console errors in browser DevTools
✅ Works on both mouse click and keyboard input

## Browser Console Check

Open DevTools (F12) and verify:
- No JavaScript errors
- SoundManager initialized successfully
- Web Audio API context created (no warnings)

## Troubleshooting

**No Sound?**
- Check if sound toggle is enabled (🔊 not 🔇)
- Verify browser allows autoplay/audio
- Check browser console for Web Audio API errors
- Try clicking sound toggle to re-enable

**Animations Not Working?**
- Verify CSS is loading correctly
- Check for browser compatibility
- Look for console errors

**Visual Issues?**
- Clear browser cache and reload
- Check if CSS animations are supported
- Try different browser

## Performance Test

1. Rapidly click multiple buttons
2. Sounds should queue naturally without crashing
3. Animations should remain smooth
4. No memory leaks (check DevTools Performance tab)

## Success Criteria

- ✅ All button types have distinct sounds
- ✅ Visual feedback on every interaction
- ✅ Sound toggle works and persists
- ✅ No lag or performance issues
- ✅ Error handling works correctly
- ✅ Keyboard and mouse input both work
- ✅ Mobile responsive (if testing on mobile)
