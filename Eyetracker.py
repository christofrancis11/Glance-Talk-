import cv2
import dlib
import numpy as np
import time
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import threading
import os

class EyeTrackingUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Eye Tracking System")
        
        # Get screen dimensions
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        
        # Configure for true fullscreen
        self.root.attributes('-fullscreen', True)
        
       # Create a style object
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TLabel', font=('Arial', 12))
        self.style.configure('RegionLabel.TLabel', font=('Arial', 14, 'bold'))
        
        # Main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create main frames with specified weights
        self.video_frame = ttk.Frame(self.main_frame)
        self.video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.control_frame = ttk.Frame(self.main_frame, width=300)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.control_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Create video label that will cover most of the screen
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Add exit button at the top of control panel for easy access
        self.exit_button = ttk.Button(self.control_frame, text="Exit Fullscreen (ESC)", command=self.exit_program)
        self.exit_button.pack(fill=tk.X, pady=(0, 20))
        
        # Control panel elements
        ttk.Label(self.control_frame, text="Eye Tracking Controls", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Status indicators with improved layout
        self.status_frame = ttk.LabelFrame(self.control_frame, text="Status")
        self.status_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Grid layout for status indicators
        self.face_status_label = ttk.Label(self.status_frame, text="Face Detection:")
        self.face_status_label.grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.face_status = ttk.Label(self.status_frame, text="Not Detected", foreground="red")
        self.face_status.grid(row=0, column=1, sticky='w', pady=5, padx=5)
        
        self.eye_status_label = ttk.Label(self.status_frame, text="Eye Status:")
        self.eye_status_label.grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.eye_status = ttk.Label(self.status_frame, text="Not Detected", foreground="red")
        self.eye_status.grid(row=1, column=1, sticky='w', pady=5, padx=5)
        
        self.gaze_status_label = ttk.Label(self.status_frame, text="Looking At:")
        self.gaze_status_label.grid(row=2, column=0, sticky='w', pady=5, padx=5)
        self.gaze_status = ttk.Label(self.status_frame, text="None", foreground="blue")
        self.gaze_status.grid(row=2, column=1, sticky='w', pady=5, padx=5)
        
        self.lock_status_label = ttk.Label(self.status_frame, text="Selection:")
        self.lock_status_label.grid(row=3, column=0, sticky='w', pady=5, padx=5)
        self.lock_status = ttk.Label(self.status_frame, text="None", foreground="blue")
        self.lock_status.grid(row=3, column=1, sticky='w', pady=5, padx=5)
        
        # Add debug info section
        self.debug_frame = ttk.LabelFrame(self.control_frame, text="Debug Info")
        self.debug_frame.pack(fill=tk.X, pady=10, padx=5)
        
        self.ear_info = ttk.Label(self.debug_frame, text="EAR: 0.00")
        self.ear_info.pack(anchor='w', pady=2)
        
        self.gaze_coord_info = ttk.Label(self.debug_frame, text="Gaze Coords: (0, 0)")
        self.gaze_coord_info.pack(anchor='w', pady=2)
        
        self.fps_info = ttk.Label(self.debug_frame, text="FPS: 0")
        self.fps_info.pack(anchor='w', pady=2)
        
        # Settings with improved layout
        self.settings_frame = ttk.LabelFrame(self.control_frame, text="Settings")
        self.settings_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Lock time setting
        ttk.Label(self.settings_frame, text="Lock Time (s):").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.lock_time_var = tk.DoubleVar(value=2.0)  # Reduced default time for faster selection
        self.lock_time_slider = ttk.Scale(self.settings_frame, from_=0.5, to=5.0, 
                                         orient=tk.HORIZONTAL, variable=self.lock_time_var)
        self.lock_time_slider.grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        self.lock_time_value = ttk.Label(self.settings_frame, text="2.0")
        self.lock_time_value.grid(row=0, column=2, sticky='w', pady=5, padx=5)
        self.lock_time_slider.bind("<Motion>", self.update_lock_time_value)
        
        # EAR threshold setting
        ttk.Label(self.settings_frame, text="EAR Threshold:").grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.ear_threshold_var = tk.DoubleVar(value=0.2)
        self.ear_threshold_slider = ttk.Scale(self.settings_frame, from_=0.1, to=0.4, 
                                             orient=tk.HORIZONTAL, variable=self.ear_threshold_var)
        self.ear_threshold_slider.grid(row=1, column=1, sticky='ew', pady=5, padx=5)
        self.ear_threshold_value = ttk.Label(self.settings_frame, text="0.2")
        self.ear_threshold_value.grid(row=1, column=2, sticky='w', pady=5, padx=5)
        self.ear_threshold_slider.bind("<Motion>", self.update_ear_threshold_value)
        
        # Gaze sensitivity setting (new)
        ttk.Label(self.settings_frame, text="Gaze Sensitivity:").grid(row=2, column=0, sticky='w', pady=5, padx=5)
        self.gaze_sensitivity_var = tk.DoubleVar(value=1.0)
        self.gaze_sensitivity_slider = ttk.Scale(self.settings_frame, from_=0.5, to=2.0, 
                                                orient=tk.HORIZONTAL, variable=self.gaze_sensitivity_var)
        self.gaze_sensitivity_slider.grid(row=2, column=1, sticky='ew', pady=5, padx=5)
        self.gaze_sensitivity_value = ttk.Label(self.settings_frame, text="1.0")
        self.gaze_sensitivity_value.grid(row=2, column=2, sticky='w', pady=5, padx=5)
        self.gaze_sensitivity_slider.bind("<Motion>", self.update_gaze_sensitivity_value)
        
        # Region size setting (new)
        ttk.Label(self.settings_frame, text="Region Size:").grid(row=3, column=0, sticky='w', pady=5, padx=5)
        self.region_size_var = tk.IntVar(value=150)
        self.region_size_slider = ttk.Scale(self.settings_frame, from_=100, to=250, 
                                           orient=tk.HORIZONTAL, variable=self.region_size_var)
        self.region_size_slider.grid(row=3, column=1, sticky='ew', pady=5, padx=5)
        self.region_size_value = ttk.Label(self.settings_frame, text="150")
        self.region_size_value.grid(row=3, column=2, sticky='w', pady=5, padx=5)
        self.region_size_slider.bind("<Motion>", self.update_region_size_value)
        self.region_size_slider.bind("<ButtonRelease-1>", self.update_regions)
        
        # Available options for eye selection
        self.options_frame = ttk.LabelFrame(self.control_frame, text="Available Options")
        self.options_frame.pack(fill=tk.X, pady=10, padx=5)
        
        self.regions_listbox = tk.Listbox(self.options_frame, height=6, font=('Arial', 10))
        self.regions_listbox.pack(fill=tk.X, pady=5)
        
        # Add option to add custom region
        self.add_region_frame = ttk.Frame(self.options_frame)
        self.add_region_frame.pack(fill=tk.X, pady=5)
        
        self.new_region_var = tk.StringVar()
        self.new_region_entry = ttk.Entry(self.add_region_frame, textvariable=self.new_region_var)
        self.new_region_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.add_region_button = ttk.Button(self.add_region_frame, text="Add", command=self.add_custom_region)
        self.add_region_button.pack(side=tk.RIGHT, padx=5)
        
        # Buttons 
        self.buttons_frame = ttk.Frame(self.control_frame)
        self.buttons_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(self.buttons_frame, text="Start Tracking", command=self.start_tracking)
        self.start_button.pack(fill=tk.X, pady=5)
        
        self.stop_button = ttk.Button(self.buttons_frame, text="Stop Tracking", command=self.stop_tracking, state=tk.DISABLED)
        self.stop_button.pack(fill=tk.X, pady=5)
        
        self.calibrate_button = ttk.Button(self.buttons_frame, text="Calibrate", command=self.calibrate_tracking)
        self.calibrate_button.pack(fill=tk.X, pady=5)
        
        # Add a status progress bar
        self.progress_bar = ttk.Progressbar(self.control_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5, padx=5)
        
        self.status_message = ttk.Label(self.control_frame, text="Idle", font=('Arial', 9))
        self.status_message.pack(pady=5)
        
        # Initialize class variables
        self.cap = None
        self.running = False
        self.thread = None
        self.calibration_mode = False
        
        # Initialize the regions (will be updated based on screen size)
        self.update_regions()
        
        # Add overlay regions directly on the video frame
        self.region_labels = {}
        self.create_region_overlays()
        
        # Eye tracking variables
        self.face_detector = None
        self.landmark_predictor = None
        self.lock_start_time = None
        self.locked_region = None
        self.last_eye_open_time = None
        self.eye_closed_duration = 0
        self.current_ear = 0
        
        # New variables for improved gaze tracking
        self.gaze_history = []
        self.gaze_history_max = 10  # frames to average
        self.last_frame_time = time.time()
        self.fps = 0
        
        # Calibration variables
        self.calibration_points = [(0.1, 0.1), (0.9, 0.1), (0.5, 0.5), (0.1, 0.9), (0.9, 0.9)]
        self.calibration_current = 0
        self.calibration_data = {}
        self.calibration_offset_x = 0
        self.calibration_offset_y = 0
        self.calibration_scale_x = 1.0
        self.calibration_scale_y = 1.0
        
        # Initialize the detector and predictor
        self.initialize_detector()
        
        # Key bindings
        self.root.bind("<Escape>", lambda e: self.exit_program())
        self.root.bind("<space>", lambda e: self.toggle_tracking())
        
        # Create a protocol for the window close event
        root.protocol("WM_DELETE_WINDOW", self.exit_program)
    
    def toggle_tracking(self):
        """Toggle tracking on/off with spacebar"""
        if self.running:
            self.stop_tracking()
        else:
            self.start_tracking()
    
    def update_regions(self, event=None):
        """Update regions based on screen size and region size setting"""
        region_size = self.region_size_var.get()
        margin = 50  # margin from the edge of the screen
        
        # Calculate center region position and size
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Define regions - positioned at corners and center of the screen
        self.regions = {
            "Food": (self.screen_width - margin - region_size, margin, 
                    self.screen_width - margin, margin + region_size),  # Top right
                    
            "Water": (margin, margin, 
                     margin + region_size, margin + region_size),  # Top left
                     
            "Medicine": (self.screen_width - margin - region_size, self.screen_height - margin - region_size, 
                        self.screen_width - margin, self.screen_height - margin),  # Bottom right
                        
            "Help": (margin, self.screen_height - margin - region_size, 
                    margin + region_size, self.screen_height - margin),  # Bottom left
                    
            "Rest": (center_x - region_size//2, center_y - region_size//2, 
                    center_x + region_size//2, center_y + region_size//2),  # Center
        }
        
        # Update regions listbox
        self.regions_listbox.delete(0, tk.END)
        for region in self.regions.keys():
            self.regions_listbox.insert(tk.END, region)
            
        # Update region overlays
        self.update_region_overlays()
    
    def create_region_overlays(self):
        """Create overlay labels for regions"""
        for region_name in self.regions.keys():
            label = ttk.Label(self.video_label, text=region_name, 
                            style='RegionLabel.TLabel', background="#333333")
            self.region_labels[region_name] = label
    
    def update_region_overlays(self):
        """Update position of region overlay labels"""
        if hasattr(self, 'region_labels'):
            for region_name, (x1, y1, x2, y2) in self.regions.items():
                if region_name in self.region_labels:
                    self.region_labels[region_name].place(
                        x=x1, y=y1, 
                        width=x2-x1, height=y2-y1
                    )
    
    def add_custom_region(self):
        """Add a custom region from user input"""
        new_region = self.new_region_var.get().strip()
        if new_region and new_region not in self.regions:
            # Calculate a position for the new region
            # Place it in the middle left area
            mid_height = self.screen_height // 2
            region_size = self.region_size_var.get()
            margin = 50  # Define margin here
            
            self.regions[new_region] = (
                margin, 
                mid_height - region_size//2, 
                margin + region_size, 
                mid_height + region_size//2
            )
            
            # Add to listbox
            self.regions_listbox.insert(tk.END, new_region)
            
            # Create overlay label
            label = ttk.Label(self.video_label, text=new_region, 
                            style='RegionLabel.TLabel', background="#333333")
            self.region_labels[new_region] = label
            self.update_region_overlays()
            
            # Clear entry
            self.new_region_var.set("")
    
    def initialize_detector(self):
        """Initialize the face detector and predictor"""
        try:
            self.face_detector = dlib.get_frontal_face_detector()
            
            # Check if the shape predictor file exists, if not, show an error
            predictor_path = "shape_predictor_68_face_landmarks.dat"
            if not os.path.exists(predictor_path):
                messagebox.showerror("File Not Found", 
                                    f"Could not find the shape predictor file at: {predictor_path}\n\n"
                                    "Please download it from:\n"
                                    "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
                self.root.quit()
                return
                
            self.landmark_predictor = dlib.shape_predictor(predictor_path)
            self.update_status("Eye tracking system initialized successfully!")
        
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize trackers: {str(e)}")
            self.root.quit()
    
    def update_status(self, message):
        """Update status message with optional auto clear"""
        self.status_message.config(text=message)
    
    def update_lock_time_value(self, event):
        """Update the lock time value label"""
        value = self.lock_time_var.get()
        self.lock_time_value.config(text=f"{value:.1f}")
    
    def update_ear_threshold_value(self, event):
        """Update the EAR threshold value label"""
        value = self.ear_threshold_var.get()
        self.ear_threshold_value.config(text=f"{value:.2f}")
    
    def update_gaze_sensitivity_value(self, event):
        """Update the gaze sensitivity value label"""
        value = self.gaze_sensitivity_var.get()
        self.gaze_sensitivity_value.config(text=f"{value:.1f}")
    
    def update_region_size_value(self, event):
        """Update the region size value label"""
        value = self.region_size_var.get()
        self.region_size_value.config(text=f"{value}")
    
    def calibrate_tracking(self):
        """Start the calibration process"""
        if not self.running:
            messagebox.showinfo("Calibration", 
                               "Calibration will help improve gaze tracking accuracy.\n\n"
                               "Look at each point that appears on screen and blink to confirm.")
            self.start_tracking(calibration=True)
        else:
            # Switch to calibration mode if already running
            self.calibration_mode = True
            self.calibration_current = 0
            self.calibration_data = {}
            self.update_status("Calibration started. Follow the points and blink to confirm.")
    
    def start_tracking(self, calibration=False):
        """Start the eye tracking process"""
        if not self.running:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Camera Error", "Could not access the webcam.")
                return
            
            self.running = True
            self.calibration_mode = calibration
            
            if calibration:
                self.calibration_current = 0
                self.calibration_data = {}
                self.update_status("Calibration started. Follow the points and blink to confirm.")
            
            self.thread = threading.Thread(target=self.tracking_loop)
            self.thread.daemon = True
            self.thread.start()
            
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.calibrate_button.config(state=tk.DISABLED)
    
    def stop_tracking(self):
        """Stop the eye tracking process"""
        self.running = False
        self.calibration_mode = False
        
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.calibrate_button.config(state=tk.NORMAL)
        
        # Reset the video label
        self.video_label.config(image='')
        
        # Reset status indicators
        self.face_status.config(text="Not Detected", foreground="red")
        self.eye_status.config(text="Not Detected", foreground="red")
        self.gaze_status.config(text="None", foreground="blue")
        self.lock_status.config(text="None", foreground="blue")
        
        # Reset progress bar
        self.progress_bar['value'] = 0
        self.update_status("Tracking stopped")
    
    def exit_program(self):
        """Exit the program cleanly"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        self.root.attributes('-fullscreen', False)  # Exit fullscreen mode
        self.root.destroy()
    
    def eye_aspect_ratio(self, landmarks):
        """Calculate eye aspect ratio (EAR) for detecting eye closure"""
        # Get the coordinates for the left eye (landmarks 36 to 41)
        left_eye = [landmarks.part(i) for i in range(36, 42)]
        # Get the coordinates for the right eye (landmarks 42 to 47)
        right_eye = [landmarks.part(i) for i in range(42, 48)]
        
        # Convert points to tuples (x, y)
        left_eye = [(point.x, point.y) for point in left_eye]
        right_eye = [(point.x, point.y) for point in right_eye]

        # Calculate the Euclidean distances between the vertical eye landmarks
        A = np.linalg.norm(np.array(left_eye[1]) - np.array(left_eye[5]))
        B = np.linalg.norm(np.array(left_eye[2]) - np.array(left_eye[4]))
        C = np.linalg.norm(np.array(right_eye[1]) - np.array(right_eye[5]))
        D = np.linalg.norm(np.array(right_eye[2]) - np.array(right_eye[4]))
        
        # Calculate the Eye Aspect Ratio (EAR) for both eyes
        left_EAR = (A + B) / (2.0 * np.linalg.norm(np.array(left_eye[0]) - np.array(left_eye[3])) + 1e-6)
        right_EAR = (C + D) / (2.0 * np.linalg.norm(np.array(right_eye[0]) - np.array(right_eye[3])) + 1e-6)
        
        # Average the two EARs
        EAR = (left_EAR + right_EAR) / 2.0
        return EAR
    
    def get_improved_gaze_direction(self, landmarks, gray, frame):
        """Calculate gaze direction with improved algorithm"""
        # Get left and right eye landmarks
        left_eye = [landmarks.part(i) for i in range(36, 42)]
        right_eye = [landmarks.part(i) for i in range(42, 48)]
        
        # Process both eyes and average the results
        left_gaze = self.process_eye_for_gaze(left_eye, gray, frame)
        right_gaze = self.process_eye_for_gaze(right_eye, gray, frame)
        
        # Get sensitivity factor
        sensitivity = self.gaze_sensitivity_var.get()
        
        # Apply calibration and sensitivity
        gaze_x = ((left_gaze[0] + right_gaze[0]) / 2) 
        gaze_y = ((left_gaze[1] + right_gaze[1]) / 2)
        
        # Apply calibration offsets and scaling
        gaze_x = (gaze_x * self.calibration_scale_x) + self.calibration_offset_x
        gaze_y = (gaze_y * self.calibration_scale_y) + self.calibration_offset_y
        
        # Apply sensitivity factor - reduces the center bias
        gaze_x = 0.5 + (gaze_x - 0.5) * sensitivity
        gaze_y = 0.5 + (gaze_y - 0.5) * sensitivity
        
        # Ensure values are within 0-1 range
        gaze_x = max(0, min(1, gaze_x))
        gaze_y = max(0, min(1, gaze_y))
        
        return gaze_x, gaze_y
    
    def process_eye_for_gaze(self, eye_landmarks, gray, frame):
        """Process a single eye for gaze estimation"""
        # Convert landmarks to numpy array
        eye_points = np.array([(point.x, point.y) for point in eye_landmarks])
        
        # Get eye region
        x_min, y_min = np.min(eye_points, axis=0)
        x_max, y_max = np.max(eye_points, axis=0)
        
        # Add padding
        padding = 5
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(gray.shape[1], x_max + padding)
        y_max = min(gray.shape[0], y_max + padding)
        
        # Check if dimensions are valid
        if x_min >= x_max or y_min >= y_max:
            return 0.5, 0.5
        
        # Extract eye region
        eye_region = gray[y_min:y_max, x_min:x_max]
        if eye_region.size == 0:
            return 0.5, 0.5
        
        # Improve contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        eye_region = clahe.apply(eye_region)
        
        # Apply Gaussian blur
        eye_region = cv2.GaussianBlur(eye_region, (7, 7), 0)
        
        # Use adaptive thresholding for better pupil detection
        _, thresholded = cv2.threshold(eye_region, 30, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        
        # Denoise
        kernel = np.ones((3, 3), np.uint8)
        thresholded = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel, iterations=1)
        thresholded = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Find the darkest region (pupil)
        contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw the contours for debugging
        eye_region_color = cv2.cvtColor(eye_region, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(eye_region_color, contours, -1, (0, 255, 0), 1)
        
        # Calculate relative position
        eye_center_x = (x_max + x_min) / 2
        eye_center_y = (y_max + y_min) / 2
        
        if contours:
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Find the center of the contour
            M = cv2.moments(largest_contour)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                
                # Draw the pupil center for debugging
                cv2.circle(eye_region_color, (cx, cy), 3, (0, 0, 255), -1)
                
                # Calculate pupil position relative to eye center
                pupil_x = x_min + cx
                pupil_y = y_min + cy
                
                # Convert to relative coordinates (0-1)
                rel_x = (pupil_x - eye_center_x) / (x_max - x_min) * 2
                rel_y = (pupil_y - eye_center_y) / (y_max - y_min) * 2
                
                # Map to 0-1 range
                # This inverts the direction because the pupil moves in the opposite direction of gaze
                gaze_x = 0.5 - rel_x * 0.5
                gaze_y = 0.5 - rel_y * 0.5
                
                # Display the processed eye region for debugging
                height, width = eye_region_color.shape[:2]
                scale_factor = 100 / height
                resized = cv2.resize(eye_region_color, (int(width * scale_factor), 100))
                
                # Draw a debug overlay in the corner
                h, w = frame.shape[:2]
                frame[h-100:h, 0:resized.shape[1]] = resized
                
                return gaze_x, gaze_y
        
        return 0.5, 0.5
    
    def tracking_loop(self):
        """Main eye tracking loop - runs in a separate thread"""
        self.last_frame_time = time.time()
        frame_count = 0
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                self.update_status("Error reading from camera!")
                self.stop_tracking()
                return
            
            # Flip frame horizontally for a mirror effect
            frame = cv2.flip(frame, 1)
            
            # Calculate FPS
            current_time = time.time()
            elapsed = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Update FPS every 10 frames
            frame_count += 1
            if frame_count >= 10:
                self.fps = 10 / elapsed
                frame_count = 0
                self.fps_info.config(text=f"FPS: {self.fps:.1f}")
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_detector(gray, 0)
            
            # Update face status
            if len(faces) > 0:
                self.face_status.config(text="Detected", foreground="green")
                
                # Get the largest face
                face = max(faces, key=lambda rect: rect.width() * rect.height())
                
                # Get landmarks
                landmarks = self.landmark_predictor(gray, face)
                
                # Calculate eye aspect ratio
                ear = self.eye_aspect_ratio(landmarks)
                self.current_ear = ear
                self.ear_info.config(text=f"EAR: {ear:.2f}")
                
                # Get ear threshold
                ear_threshold = self.ear_threshold_var.get()
                
                # Detect if eyes are open or closed
                if ear < ear_threshold:
                    # Eyes closed
                    if self.last_eye_open_time is not None:
                        self.eye_closed_duration = current_time - self.last_eye_open_time
                    self.eye_status.config(text="Closed", foreground="red")
                    
                    # Handle eye blink for calibration
                    if self.calibration_mode and self.eye_closed_duration > 0.2:
                        self.process_calibration_point()
                else:
                    # Eyes open
                    self.last_eye_open_time = current_time
                    self.eye_closed_duration = 0
                    self.eye_status.config(text="Open", foreground="green")
                
                # Get gaze direction
                gaze_x, gaze_y = self.get_improved_gaze_direction(landmarks, gray, frame)
                
                # Apply temporal smoothing
                self.gaze_history.append((gaze_x, gaze_y))
                if len(self.gaze_history) > self.gaze_history_max:
                    self.gaze_history.pop(0)
                
                # Average the gaze positions
                avg_gaze_x = sum(g[0] for g in self.gaze_history) / len(self.gaze_history)
                avg_gaze_y = sum(g[1] for g in self.gaze_history) / len(self.gaze_history)
                
                # Map to screen coordinates
                screen_x = int(avg_gaze_x * self.screen_width)
                screen_y = int(avg_gaze_y * self.screen_height)
                
                # Update gaze coordinates display
                self.gaze_coord_info.config(text=f"Gaze Coords: ({screen_x}, {screen_y})")
                
                # If in calibration mode, draw calibration point
                if self.calibration_mode and self.calibration_current < len(self.calibration_points):
                    calib_point = self.calibration_points[self.calibration_current]
                    calib_x = int(calib_point[0] * self.screen_width)
                    calib_y = int(calib_point[1] * self.screen_height)
                    
                    # Draw calibration point
                    cv2.circle(frame, (calib_x, calib_y), 20, (0, 255, 0), -1)
                    cv2.circle(frame, (calib_x, calib_y), 22, (255, 255, 255), 2)
                    
                    # Draw instruction text
                    cv2.putText(frame, "Look at the green dot and blink", 
                               (int(self.screen_width/2 - 200), 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                else:
                    # Check which region is being gazed at
                    current_region = None
                    for name, (x1, y1, x2, y2) in self.regions.items():
                        if x1 <= screen_x <= x2 and y1 <= screen_y <= y2:
                            current_region = name
                            break
                    
                    # Update gaze status
                    if current_region:
                        self.gaze_status.config(text=current_region, foreground="blue")
                        
                        # Highlight the current region
                        for region_name, label in self.region_labels.items():
                            if region_name == current_region:
                                label.configure(background="#88CC88")  # Green background for active region
                            else:
                                label.configure(background="#333333")  # Default background (no alpha)

                        
                        # Check for gaze lock on region
                        if self.locked_region != current_region:
                            self.locked_region = current_region
                            self.lock_start_time = current_time
                        else:
                            # Calculate progress towards selection
                            if self.lock_start_time is not None:
                                lock_duration = current_time - self.lock_start_time
                                lock_time = self.lock_time_var.get()
                                
                                # Update progress bar
                                progress = min(100, (lock_duration / lock_time) * 100)
                                self.progress_bar['value'] = progress
                                
                                # Check if gaze lock is complete
                                if lock_duration >= lock_time:
                                    self.make_selection(current_region)
                                    # Reset lock
                                    self.lock_start_time = current_time
                    else:
                        self.gaze_status.config(text="None", foreground="blue")
                        self.locked_region = None
                        self.lock_start_time = None
                        self.progress_bar['value'] = 0
                        
                        # Reset all region highlights
                        for label in self.region_labels.values():
                            label.configure(background="#333333")
                
                # Draw eye landmarks and gaze direction
                self.draw_eye_tracking_debug(frame, landmarks, (avg_gaze_x, avg_gaze_y))
            else:
                self.face_status.config(text="Not Detected", foreground="red")
                self.eye_status.config(text="Not Detected", foreground="red")
                self.gaze_status.config(text="None", foreground="blue")
                self.locked_region = None
                self.lock_start_time = None
                self.progress_bar['value'] = 0
            
            # Convert frame to format for tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update the video label
            self.video_label.config(image=imgtk)
            self.video_label.image = imgtk  # Keep a reference to prevent garbage collection
    
    def draw_eye_tracking_debug(self, frame, landmarks, gaze):
        """Draw eye landmarks and gaze direction for debugging"""
        # Draw face landmarks
        for n in range(36, 48):  # Eye landmarks
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        
        # Draw estimated gaze point
        screen_x = int(gaze[0] * self.screen_width)
        screen_y = int(gaze[1] * self.screen_height)
        cv2.circle(frame, (screen_x, screen_y), 10, (0, 0, 255), -1)
    
    def make_selection(self, region):
        """Handle selection of a region"""
        self.lock_status.config(text=region, foreground="green")
        self.update_status(f"Selected: {region}")
        
        # Play a sound to indicate selection
        self.root.bell()
        
        # Here you would add code to perform actions based on the selected region
        # For example, send notifications, trigger events, etc.
    
    def process_calibration_point(self):
        """Process the current calibration point"""
        if self.calibration_current < len(self.calibration_points):
            # Get the expected point
            point = self.calibration_points[self.calibration_current]
            
            # Get the current gaze point (average of gaze history)
            if self.gaze_history:
                avg_gaze_x = sum(g[0] for g in self.gaze_history) / len(self.gaze_history)
                avg_gaze_y = sum(g[1] for g in self.gaze_history) / len(self.gaze_history)
                
                # Store the calibration data
                self.calibration_data[point] = (avg_gaze_x, avg_gaze_y)
                
                # Move to next point
                self.calibration_current += 1
                
                if self.calibration_current < len(self.calibration_points):
                    self.update_status(f"Calibration point {self.calibration_current+1}/{len(self.calibration_points)}. Look at the green dot and blink.")
                else:
                    # Calibration complete, calculate calibration parameters
                    self.calculate_calibration_parameters()
                    self.calibration_mode = False
                    self.update_status("Calibration complete! Tracking resumed.")
    
    def calculate_calibration_parameters(self):
        """Calculate calibration parameters from collected data"""
        if len(self.calibration_data) < 3:
            # Not enough data points
            self.update_status("Calibration failed: Not enough data points!")
            return
        
        # Calculate average offsets and scaling
        x_offsets = []
        y_offsets = []
        x_scales = []
        y_scales = []
        
        for (expected_x, expected_y), (actual_x, actual_y) in self.calibration_data.items():
            # Calculate offset (difference between expected and actual)
            x_offset = expected_x - actual_x
            y_offset = expected_y - actual_y
            
            # Calculate scaling (ratio of expected to actual distance from center)
            x_scale = abs(expected_x - 0.5) / (abs(actual_x - 0.5) + 1e-6)
            y_scale = abs(expected_y - 0.5) / (abs(actual_y - 0.5) + 1e-6)
            
            x_offsets.append(x_offset)
            y_offsets.append(y_offset)
            x_scales.append(x_scale)
            y_scales.append(y_scale)
        
        # Average the parameters
        self.calibration_offset_x = sum(x_offsets) / len(x_offsets)
        self.calibration_offset_y = sum(y_offsets) / len(y_offsets)
        self.calibration_scale_x = sum(x_scales) / len(x_scales)
        self.calibration_scale_y = sum(y_scales) / len(y_scales)
        
        # Log the calibration parameters
        calibration_info = (
            f"Calibration complete!\n"
            f"X Offset: {self.calibration_offset_x:.3f}, Y Offset: {self.calibration_offset_y:.3f}\n"
            f"X Scale: {self.calibration_scale_x:.3f}, Y Scale: {self.calibration_scale_y:.3f}"
        )
        print(calibration_info)


# If running directly, start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = EyeTrackingUI(root)
    root.mainloop()