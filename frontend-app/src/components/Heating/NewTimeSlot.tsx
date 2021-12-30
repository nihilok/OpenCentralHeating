import * as React from "react";

interface Props {}

export function NewTimeSlot(props: Props) {
  const hours = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23,
  ];

  const mouseDown = React.useRef<number>(0)

  const handleTimeSlotClick = (event: React.MouseEvent<any> | React.TouchEvent<any>) => {
    const target = event.target as HTMLElement;
    target.style.backgroundColor = target.style.backgroundColor === "firebrick" ? 'white' : 'firebrick';
  };

  const handleTouchMove = (event: React.TouchEvent) => {
      const myLocation = event.touches[0];
      const target = document.elementFromPoint(myLocation.clientX, myLocation.clientY) as HTMLElement;
      target.style.backgroundColor = target.style.backgroundColor === "firebrick" ? 'white' : 'firebrick';
  }

  const handleMouseOver = (event: React.MouseEvent) => {
    if (mouseDown.current) {
      const target = event.target as HTMLElement;
      target.style.backgroundColor = "firebrick";
    }
  }

  React.useEffect(() => {

    document.documentElement.onmousedown = function() {
      ++mouseDown.current
    }

    document.documentElement.onmouseup = function() {
      --mouseDown.current
    }
  }, [])

  return (
    <div
      className="time-slot-picker__wrapper"
      onMouseDown={handleTimeSlotClick}
      onMouseUp={handleTimeSlotClick}
      onTouchMove={handleTouchMove}
      onTouchStart={handleTimeSlotClick}
      onMouseOver={handleMouseOver}
    >
      <div className="time-slot__labels">
        {hours.map((h: number) => (
          <div>{h}</div>
        ))}
      </div>
      <div className="time-slot__bars">
        {hours.map((h: number) => (
          <div
            id={`time-slot-bar-${h}`}
            onClick={handleTimeSlotClick}
          />
        ))}
      </div>
    </div>
  );
}
