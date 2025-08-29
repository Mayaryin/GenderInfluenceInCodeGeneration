from helpers.Message import Message

CONVERSATION_ID = 19
USER_ID = 63
MODEL_VERSION = "ChatGPT 4o"

message_0 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text="""
        def remove_fast_irregular_vectors(flow, magnitude_threshold=0.7, angle_threshold_deg=15):
            fx = flow[:, :, 0]
            fy = flow[:, :, 1]
            magnitude = np.sqrt(fx ** 2 + fy ** 2)
            angle = np.arctan2(fy, fx)
        
            # Lokale Mittelwerte von Richtung und Betrag (über 3x3 Fenster)
            angle_mean = uniform_filter(angle, size=3)
            magnitude_mean = uniform_filter(magnitude, size=3)
        
            # Winkelabweichung berechnen
            angle_diff = np.abs(angle - angle_mean)
            angle_diff = np.where(angle_diff > np.pi, 2 * np.pi - angle_diff, angle_diff)
        
            # Schwellenwerte
            angle_threshold = np.deg2rad(angle_threshold_deg)
        
            # Maske für rauszufilternde Vektoren:
            mask = (magnitude > magnitude_mean + magnitude_threshold) & (angle_diff > angle_threshold)
        
            flow_filtered = flow.copy()
            flow_filtered[mask] = 0  # setze unregelmäßige, schnelle Vektoren auf 0
        
            return flow_filtered
        
        def match_block(args):
            y, x, prev, curr, block_size, search_range = args
            block = prev[y:y + block_size, x:x + block_size]
            s = search_range
            offset_x, offset_y = 0, 0
        
            while s >= 1:
                min_diff = float('inf')
                best_dx, best_dy = 0, 0
        
                for dy in range(-s, s + 1, s):
                    for dx in range(-s, s + 1, s):
                        ny = y + offset_y + dy
                        nx = x + offset_x + dx
                        candidate = curr[ny:ny + block_size, nx:nx + block_size]
        
                        if candidate.shape != block.shape:
                            continue
        
                        diff = np.sum((block - candidate) ** 2)
                        if diff < min_diff:
                            min_diff = diff
                            best_dx = dx
                            best_dy = dy
        
                offset_x += best_dx
                offset_y += best_dy
                s //= 2
        
            return (y, x, offset_x, offset_y)
        
        
        def block_matching_tss_parallel(prev, curr, block_size, search_range):
            h, w = prev.shape
            flow = np.zeros((h, w, 2), dtype=np.float32)
        
            block_positions = [
                (y, x, prev, curr, block_size, search_range)
                for y in range(0, h - block_size, block_size)
                for x in range(0, w - block_size, block_size)
            ]
        
            with ThreadPoolExecutor() as executor:
                results = executor.map(match_block, block_positions)
        
            for y, x, dx, dy in results:
                flow[y:y + block_size, x:x + block_size] = (dx, dy)
        
            return flow
        
        
        def main():
            # Parameters (Aljosha Video)
            x1, x2 = 200, 550
            y1, y2 = 0, 350
            block_size = 16
            search_range = 21
            zoom_factor = 4
            frame_skip = 3
        
            video_path = r"/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/A2.mp4"
        
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
        
            # Video segment
            start_sec = 5 * 60 + 4
            end_sec = 5 * 60 + 8
        
            start_frame = int(start_sec * fps)
            end_frame = int(end_sec * fps)
        
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
            ret, prev_frame = cap.read()
            if not ret:
                raise RuntimeError("Error reading video")
        
            prev_gray = cv2.cvtColor(prev_frame[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
            prev_gray_zoomed = scipy_zoom(prev_gray, zoom_factor, order=3, mode='constant', cval=0.0, prefilter=True)
        
            current_frame = start_frame
            print(f"Processing frames {start_frame} to {end_frame}...")
            print(f"FPS: {fps}")
        
            gif_frames = []
            speed_records = []
        
            while cap.isOpened() and current_frame < end_frame:
                ret, frame = cap.read()
                if not ret:
                    break
        
                if (current_frame - start_frame) % frame_skip != 0:
                    current_frame += 1
                    continue
        
                frame = frame[y1:y2, x1:x2]
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray_zoomed = scipy_zoom(gray, zoom_factor, order=3, mode='constant', cval=0.0, prefilter=True)
        
                flow = block_matching_tss_parallel(prev_gray_zoomed, gray_zoomed, block_size, search_range)
        
                fx = flow[:, :, 0]
                fy = flow[:, :, 1]
                mask1 = (fy > 1) & (np.abs(fy) > 2 * np.abs(fx))
                flow_masked = np.zeros_like(flow)
                flow_masked[mask1] = flow[mask1]
                flow_filtered = remove_fast_irregular_vectors(flow_masked)
        
                filtered_magnitude = np.linalg.norm(flow_filtered, axis=2)
                avg_magnitude = np.mean(filtered_magnitude)
                std_magnitude = np.std(filtered_magnitude)
                se_magnitude = std_magnitude / np.sqrt(filtered_magnitude.size)
                timestamp = current_frame / fps
                
                #avg_magnitude = np.mean(magnitude)
                #std_magnitude = np.std(magnitude)
                #se_magnitude = std_magnitude / np.sqrt(magnitude.size)
                #timestamp = current_frame / fps
        
                print(f"Frame {current_frame}: Mean = {avg_magnitude:.2f}, Std = {std_magnitude:.2f}, SE = {se_magnitude:.4f}")
                speed_records.append((timestamp, avg_magnitude, std_magnitude, se_magnitude))
        
                vis_frame = cv2.resize(frame, (gray_zoomed.shape[1], gray_zoomed.shape[0]))
                for y in range(0, flow_filtered.shape[0], block_size):
                    for x in range(0, flow_filtered.shape[1], block_size):
                        dx, dy = flow_filtered[y, x]
                        start_point = (x, y)
                        end_point = (int(x + dx), int(y + dy))
                        cv2.arrowedLine(vis_frame, start_point, end_point, color=(0, 255, 0), thickness=1, tipLength=0.3)
        
                label = f"t = {timestamp:.2f}s, speed = {avg_magnitude:.2f} pixels/frame"
                cv2.putText(vis_frame, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
                gif_frames.append(cv2.cvtColor(vis_frame, cv2.COLOR_BGR2RGB))
                prev_gray_zoomed = gray_zoomed
                current_frame += 1
        
            cap.release()
        
            imageio.mimsave("Aljosha_vid.gif", gif_frames, duration=1 / fps)
        
            speed_array = np.array(speed_records)
            means = speed_array[:, 1]
            stds = speed_array[:, 2]
            ses = speed_array[:, 3]
        
            var_of_means = np.var(means)
            mean_std = np.mean(stds)
            mean_se = np.mean(ses)
        
            with open("Aljosha_vid_speeds_pixels.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([])  # Empty row
                writer.writerow(["--- Summary ---"])
                writer.writerow(["Variance of the means", var_of_means])
                writer.writerow(["Mean standard deviation", mean_std])
                writer.writerow(["Mean standard error", mean_se])
        
        
            print("\n--- Summary ---")
            print(f"Variance of the means: {var_of_means:.4f}")
            print(f"Mean standard deviation: {mean_std:.4f}")
            print(f"Mean standard error: {mean_se:.4f}")
            
            times = speed_array[:, 0]
            means = speed_array[:, 1]
            stds = speed_array[:, 2]
            ses = speed_array[:, 3]
        
            plt.figure(figsize=(10, 6))
            plt.plot(times, means, label='Mean Speed', color='orange')
            plt.fill_between(times, means - stds, means + stds, color='orange', alpha=0.2, label='Std Dev')
            plt.fill_between(times, means - ses, means + ses, color='blue', alpha=0.2, label='Standard Error')
            plt.xlabel("Time (s)")
            plt.ylabel("Speed (pixels/frame)")
            plt.title("Lava Flow Speed Over Time")
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.savefig("lava_flow_speed_plot.png", dpi=300)
            plt.show()
        
        if __name__ == "__main__":
            main()
        # %%    
        #%%
        
        #Our Video
        
        
        def remove_non_linear_vectors(flow, angle_threshold_deg=15, min_magnitude=1.0):
            fx = flow[:, :, 0]
            fy = flow[:, :, 1]
            magnitude = np.sqrt(fx ** 2 + fy ** 2)
            angle = np.arctan2(fy, fx)
        
            angle_mean = uniform_filter(angle, size=3)
            angle_diff = np.abs(angle - angle_mean)
            angle_diff = np.where(angle_diff > np.pi, 2 * np.pi - angle_diff, angle_diff)
        
            angle_threshold = np.deg2rad(angle_threshold_deg)
            mask = (angle_diff < angle_threshold) & (magnitude > min_magnitude)
        
            flow_filtered = np.zeros_like(flow)
            flow_filtered[mask] = flow[mask]
        
            return flow_filtered
        
        
        def match_block(args):
            y, x, prev, curr, block_size, search_range = args
            block = prev[y:y + block_size, x:x + block_size]
            s = search_range
            offset_x, offset_y = 0, 0
        
            while s >= 1:
                min_diff = float('inf')
                best_dx, best_dy = 0, 0
        
                for dy in range(-s, s + 1, s):
                    for dx in range(-s, s + 1, s):
                        ny = y + offset_y + dy
                        nx = x + offset_x + dx
                        candidate = curr[ny:ny + block_size, nx:nx + block_size]
        
                        if candidate.shape != block.shape:
                            continue
        
                        diff = np.sum((block - candidate) ** 2)
                        if diff < min_diff:
                            min_diff = diff
                            best_dx = dx
                            best_dy = dy
        
                offset_x += best_dx
                offset_y += best_dy
                s //= 2
        
            return (y, x, offset_x, offset_y)
        
        
        def block_matching_tss_parallel(prev, curr, block_size, search_range):
            h, w = prev.shape
            flow = np.zeros((h, w, 2), dtype=np.float32)
        
            block_positions = [
                (y, x, prev, curr, block_size, search_range)
                for y in range(0, h - block_size, block_size)
                for x in range(0, w - block_size, block_size)
            ]
        
            with ThreadPoolExecutor() as executor:
                results = executor.map(match_block, block_positions)
        
            for y, x, dx, dy in results:
                flow[y:y + block_size, x:x + block_size] = (dx, dy)
        
            return flow
        
        
        def main():
            x1, x2 = 1000, 2000
            y1, y2 = 0, 600
            block_size = 16
            search_range = 7
            zoom_factor = 1
            frame_skip = 2
        
            video_path = "/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/M1.mp4"
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
        
            start_sec = 7 * 60 + 44
            end_sec = 7 * 60 + 48
            start_frame = int(start_sec * fps)
            end_frame = int(end_sec * fps)
        
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            ret, prev_frame = cap.read()
            if not ret:
                raise RuntimeError("Error reading video")
        
            prev_gray = cv2.cvtColor(prev_frame[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
            prev_gray_zoomed = scipy_zoom(prev_gray, zoom_factor, order=3, mode='constant', cval=0.0, prefilter=True)
        
            current_frame = start_frame
            print(f"Processing frames {start_frame} to {end_frame}...")
            print(f"FPS: {fps}")
        
            gif_frames = []
            speed_records = []
        
            while cap.isOpened() and current_frame < end_frame:
                ret, frame = cap.read()
                if not ret:
                    break
        
                if (current_frame - start_frame) % frame_skip != 0:
                    current_frame += 1
                    continue
        
                frame = frame[y1:y2, x1:x2]
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray_zoomed = scipy_zoom(gray, zoom_factor, order=3, mode='constant', cval=0.0, prefilter=True)
        
                flow = block_matching_tss_parallel(prev_gray_zoomed, gray_zoomed, block_size, search_range)
                flow = remove_non_linear_vectors(flow)
        
                magnitude = np.linalg.norm(flow, axis=2)
                avg_magnitude = np.mean(magnitude)
                std_magnitude = np.std(magnitude)
                se_magnitude = std_magnitude / np.sqrt(magnitude.size)
                timestamp = current_frame / fps
        
                print(f"Frame {current_frame}: Mean = {avg_magnitude:.2f}, Std = {std_magnitude:.2f}, SE = {se_magnitude:.4f}")
                speed_records.append((timestamp, avg_magnitude, std_magnitude, se_magnitude))
        
                vis_frame = cv2.resize(frame, (gray_zoomed.shape[1], gray_zoomed.shape[0]))
                for y in range(0, flow.shape[0], block_size):
                    for x in range(0, flow.shape[1], block_size):
                        dx, dy = flow[y, x]
                        start_point = (x, y)
                        end_point = (int(x + dx), int(y + dy))
                        cv2.arrowedLine(vis_frame, start_point, end_point, color=(0, 255, 0), thickness=1, tipLength=0.3)
        
                label = f"t = {timestamp:.2f}s, speed = {avg_magnitude:.2f} pixels/frame"
                cv2.putText(vis_frame, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                gif_frames.append(cv2.cvtColor(vis_frame, cv2.COLOR_BGR2RGB))
        
                prev_gray_zoomed = gray_zoomed
                current_frame += 1
        
            cap.release()
        
            imageio.mimsave("lava_flow_vectors.gif", gif_frames, duration=1 / fps)
            
            speed_array = np.array(speed_records)
            means = speed_array[:, 1]
            stds = speed_array[:, 2]
            ses = speed_array[:, 3]
        
            var_of_means = np.var(means)
            mean_std = np.mean(stds)
            mean_se = np.mean(ses)
        
            with open("our_vid_speeds_pixels.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([])  # Empty row
                writer.writerow(["--- Summary ---"])
                writer.writerow(["Variance of the means", var_of_means])
                writer.writerow(["Mean standard deviation", mean_std])
                writer.writerow(["Mean standard error", mean_se])
        
        
            print("\n--- Summary ---")
            print(f"Variance of the means: {var_of_means:.4f}")
            print(f"Mean standard deviation: {mean_std:.4f}")
            print(f"Mean standard error: {mean_se:.4f}")
            
            times = speed_array[:, 0]
            means = speed_array[:, 1]
            stds = speed_array[:, 2]
            ses = speed_array[:, 3]
        
            plt.figure(figsize=(10, 6))
            plt.plot(times, means, label='Mean Speed', color='orange')
            plt.fill_between(times, means - stds, means + stds, color='orange', alpha=0.2, label='Std Dev')
            plt.fill_between(times, means - ses, means + ses, color='blue', alpha=0.2, label='Standard Error')
            plt.xlabel("Time (s)")
            plt.ylabel("Speed (pixels/frame)")
            plt.title("Lava Flow Speed Over Time")
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.savefig("lava_flow_speed_plot.png", dpi=300)
            plt.show()
        
        
        if __name__ == "__main__":
            main()
        # %%
        #Aljosha Video
        video_path = "/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/A2.mp4"
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        
        cv2.imwrite("first_frame.png", frame)
        print(" Frame saved as 'first_frame.png'")
        
        # Get resolution
        height, width, _ = frame.shape
        print(f"Frame resolution: {width} × {height} pixels")
        
        # %%
        
        #our video
        video_path = "/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/M1.mp4"
        cap = cv2.VideoCapture(video_path)
        frame_number = 27848  # Change this to the desired frame number
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        
        cv2.imwrite("first_frame_2.png", frame)
        print("Frame saved as 'first_frame.png")
        
        height, width, _ = frame.shape
        print(f"Frame resolution: {width} × {height} pixels")
        
        can you give me a new code snipped where I just get a gif without block matching and all of the scenes I used?
        """,
    model_version="",
    message_order=0,
    conversational="can you give me a new code snipped where I just get a gif without block matching and all of the scenes I used?",
    code="""
            def remove_fast_irregular_vectors(flow, magnitude_threshold=0.7, angle_threshold_deg=15):
            fx = flow[:, :, 0]
            fy = flow[:, :, 1]
            magnitude = np.sqrt(fx ** 2 + fy ** 2)
            angle = np.arctan2(fy, fx)
        
            # Lokale Mittelwerte von Richtung und Betrag (über 3x3 Fenster)
            angle_mean = uniform_filter(angle, size=3)
            magnitude_mean = uniform_filter(magnitude, size=3)
        
            # Winkelabweichung berechnen
            angle_diff = np.abs(angle - angle_mean)
            angle_diff = np.where(angle_diff > np.pi, 2 * np.pi - angle_diff, angle_diff)
        
            # Schwellenwerte
            angle_threshold = np.deg2rad(angle_threshold_deg)
        
            # Maske für rauszufilternde Vektoren:
            mask = (magnitude > magnitude_mean + magnitude_threshold) & (angle_diff > angle_threshold)
        
            flow_filtered = flow.copy()
            flow_filtered[mask] = 0  # setze unregelmäßige, schnelle Vektoren auf 0
        
            return flow_filtered
        
        def match_block(args):
            y, x, prev, curr, block_size, search_range = args
            block = prev[y:y + block_size, x:x + block_size]
            s = search_range
            offset_x, offset_y = 0, 0
        
            while s >= 1:
                min_diff = float('inf')
                best_dx, best_dy = 0, 0
        
                for dy in range(-s, s + 1, s):
                    for dx in range(-s, s + 1, s):
                        ny = y + offset_y + dy
                        nx = x + offset_x + dx
                        candidate = curr[ny:ny + block_size, nx:nx + block_size]
        
                        if candidate.shape != block.shape:
                            continue
        
                        diff = np.sum((block - candidate) ** 2)
                        if diff < min_diff:
                            min_diff = diff
                            best_dx = dx
                            best_dy = dy
        
                offset_x += best_dx
                offset_y += best_dy
                s //= 2
        
            return (y, x, offset_x, offset_y)
        
        
        def block_matching_tss_parallel(prev, curr, block_size, search_range):
            h, w = prev.shape
            flow = np.zeros((h, w, 2), dtype=np.float32)
        
            block_positions = [
                (y, x, prev, curr, block_size, search_range)
                for y in range(0, h - block_size, block_size)
                for x in range(0, w - block_size, block_size)
            ]
        
            with ThreadPoolExecutor() as executor:
                results = executor.map(match_block, block_positions)
        
            for y, x, dx, dy in results:
                flow[y:y + block_size, x:x + block_size] = (dx, dy)
        
            return flow
        
        
        def main():
            # Parameters (Aljosha Video)
            x1, x2 = 200, 550
            y1, y2 = 0, 350
            block_size = 16
            search_range = 21
            zoom_factor = 4
            frame_skip = 3
        
            video_path = r"/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/A2.mp4"
        
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
        
            # Video segment
            start_sec = 5 * 60 + 4
            end_sec = 5 * 60 + 8
        
            start_frame = int(start_sec * fps)
            end_frame = int(end_sec * fps)
        
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
            ret, prev_frame = cap.read()
            if not ret:
                raise RuntimeError("Error reading video")
        
            prev_gray = cv2.cvtColor(prev_frame[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
            prev_gray_zoomed = scipy_zoom(prev_gray, zoom_factor, order=3, mode='constant', cval=0.0, prefilter=True)
        
            current_frame = start_frame
            print(f"Processing frames {start_frame} to {end_frame}...")
            print(f"FPS: {fps}")
        
            gif_frames = []
            speed_records = []
        
            while cap.isOpened() and current_frame < end_frame:
                ret, frame = cap.read()
                if not ret:
                    break
        
                if (current_frame - start_frame) % frame_skip != 0:
                    current_frame += 1
                    continue
        
                frame = frame[y1:y2, x1:x2]
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray_zoomed = scipy_zoom(gray, zoom_factor, order=3, mode='constant', cval=0.0, prefilter=True)
        
                flow = block_matching_tss_parallel(prev_gray_zoomed, gray_zoomed, block_size, search_range)
        
                fx = flow[:, :, 0]
                fy = flow[:, :, 1]
                mask1 = (fy > 1) & (np.abs(fy) > 2 * np.abs(fx))
                flow_masked = np.zeros_like(flow)
                flow_masked[mask1] = flow[mask1]
                flow_filtered = remove_fast_irregular_vectors(flow_masked)
        
                filtered_magnitude = np.linalg.norm(flow_filtered, axis=2)
                avg_magnitude = np.mean(filtered_magnitude)
                std_magnitude = np.std(filtered_magnitude)
                se_magnitude = std_magnitude / np.sqrt(filtered_magnitude.size)
                timestamp = current_frame / fps
                
                #avg_magnitude = np.mean(magnitude)
                #std_magnitude = np.std(magnitude)
                #se_magnitude = std_magnitude / np.sqrt(magnitude.size)
                #timestamp = current_frame / fps
        
                print(f"Frame {current_frame}: Mean = {avg_magnitude:.2f}, Std = {std_magnitude:.2f}, SE = {se_magnitude:.4f}")
                speed_records.append((timestamp, avg_magnitude, std_magnitude, se_magnitude))
        
                vis_frame = cv2.resize(frame, (gray_zoomed.shape[1], gray_zoomed.shape[0]))
                for y in range(0, flow_filtered.shape[0], block_size):
                    for x in range(0, flow_filtered.shape[1], block_size):
                        dx, dy = flow_filtered[y, x]
                        start_point = (x, y)
                        end_point = (int(x + dx), int(y + dy))
                        cv2.arrowedLine(vis_frame, start_point, end_point, color=(0, 255, 0), thickness=1, tipLength=0.3)
        
                label = f"t = {timestamp:.2f}s, speed = {avg_magnitude:.2f} pixels/frame"
                cv2.putText(vis_frame, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
                gif_frames.append(cv2.cvtColor(vis_frame, cv2.COLOR_BGR2RGB))
                prev_gray_zoomed = gray_zoomed
                current_frame += 1
        
            cap.release()
        
            imageio.mimsave("Aljosha_vid.gif", gif_frames, duration=1 / fps)
        
            speed_array = np.array(speed_records)
            means = speed_array[:, 1]
            stds = speed_array[:, 2]
            ses = speed_array[:, 3]
        
            var_of_means = np.var(means)
            mean_std = np.mean(stds)
            mean_se = np.mean(ses)
        
            with open("Aljosha_vid_speeds_pixels.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([])  # Empty row
                writer.writerow(["--- Summary ---"])
                writer.writerow(["Variance of the means", var_of_means])
                writer.writerow(["Mean standard deviation", mean_std])
                writer.writerow(["Mean standard error", mean_se])
        
        
            print("\n--- Summary ---")
            print(f"Variance of the means: {var_of_means:.4f}")
            print(f"Mean standard deviation: {mean_std:.4f}")
            print(f"Mean standard error: {mean_se:.4f}")
            
            times = speed_array[:, 0]
            means = speed_array[:, 1]
            stds = speed_array[:, 2]
            ses = speed_array[:, 3]
        
            plt.figure(figsize=(10, 6))
            plt.plot(times, means, label='Mean Speed', color='orange')
            plt.fill_between(times, means - stds, means + stds, color='orange', alpha=0.2, label='Std Dev')
            plt.fill_between(times, means - ses, means + ses, color='blue', alpha=0.2, label='Standard Error')
            plt.xlabel("Time (s)")
            plt.ylabel("Speed (pixels/frame)")
            plt.title("Lava Flow Speed Over Time")
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.savefig("lava_flow_speed_plot.png", dpi=300)
            plt.show()
        
        if __name__ == "__main__":
            main()
        # %%    
        #%%
        
        #Our Video
        
        
        def remove_non_linear_vectors(flow, angle_threshold_deg=15, min_magnitude=1.0):
            fx = flow[:, :, 0]
            fy = flow[:, :, 1]
            magnitude = np.sqrt(fx ** 2 + fy ** 2)
            angle = np.arctan2(fy, fx)
        
            angle_mean = uniform_filter(angle, size=3)
            angle_diff = np.abs(angle - angle_mean)
            angle_diff = np.where(angle_diff > np.pi, 2 * np.pi - angle_diff, angle_diff)
        
            angle_threshold = np.deg2rad(angle_threshold_deg)
            mask = (angle_diff < angle_threshold) & (magnitude > min_magnitude)
        
            flow_filtered = np.zeros_like(flow)
            flow_filtered[mask] = flow[mask]
        
            return flow_filtered
        
        
        def match_block(args):
            y, x, prev, curr, block_size, search_range = args
            block = prev[y:y + block_size, x:x + block_size]
            s = search_range
            offset_x, offset_y = 0, 0
        
            while s >= 1:
                min_diff = float('inf')
                best_dx, best_dy = 0, 0
        
                for dy in range(-s, s + 1, s):
                    for dx in range(-s, s + 1, s):
                        ny = y + offset_y + dy
                        nx = x + offset_x + dx
                        candidate = curr[ny:ny + block_size, nx:nx + block_size]
        
                        if candidate.shape != block.shape:
                            continue
        
                        diff = np.sum((block - candidate) ** 2)
                        if diff < min_diff:
                            min_diff = diff
                            best_dx = dx
                            best_dy = dy
        
                offset_x += best_dx
                offset_y += best_dy
                s //= 2
        
            return (y, x, offset_x, offset_y)
        
        
        def block_matching_tss_parallel(prev, curr, block_size, search_range):
            h, w = prev.shape
            flow = np.zeros((h, w, 2), dtype=np.float32)
        
            block_positions = [
                (y, x, prev, curr, block_size, search_range)
                for y in range(0, h - block_size, block_size)
                for x in range(0, w - block_size, block_size)
            ]
        
            with ThreadPoolExecutor() as executor:
                results = executor.map(match_block, block_positions)
        
            for y, x, dx, dy in results:
                flow[y:y + block_size, x:x + block_size] = (dx, dy)
        
            return flow
        
        
        def main():
            x1, x2 = 1000, 2000
            y1, y2 = 0, 600
            block_size = 16
            search_range = 7
            zoom_factor = 1
            frame_skip = 2
        
            video_path = "/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/M1.mp4"
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
        
            start_sec = 7 * 60 + 44
            end_sec = 7 * 60 + 48
            start_frame = int(start_sec * fps)
            end_frame = int(end_sec * fps)
        
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            ret, prev_frame = cap.read()
            if not ret:
                raise RuntimeError("Error reading video")
        
            prev_gray = cv2.cvtColor(prev_frame[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
            prev_gray_zoomed = scipy_zoom(prev_gray, zoom_factor, order=3, mode='constant', cval=0.0, prefilter=True)
        
            current_frame = start_frame
            print(f"Processing frames {start_frame} to {end_frame}...")
            print(f"FPS: {fps}")
        
            gif_frames = []
            speed_records = []
        
            while cap.isOpened() and current_frame < end_frame:
                ret, frame = cap.read()
                if not ret:
                    break
        
                if (current_frame - start_frame) % frame_skip != 0:
                    current_frame += 1
                    continue
        
                frame = frame[y1:y2, x1:x2]
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray_zoomed = scipy_zoom(gray, zoom_factor, order=3, mode='constant', cval=0.0, prefilter=True)
        
                flow = block_matching_tss_parallel(prev_gray_zoomed, gray_zoomed, block_size, search_range)
                flow = remove_non_linear_vectors(flow)
        
                magnitude = np.linalg.norm(flow, axis=2)
                avg_magnitude = np.mean(magnitude)
                std_magnitude = np.std(magnitude)
                se_magnitude = std_magnitude / np.sqrt(magnitude.size)
                timestamp = current_frame / fps
        
                print(f"Frame {current_frame}: Mean = {avg_magnitude:.2f}, Std = {std_magnitude:.2f}, SE = {se_magnitude:.4f}")
                speed_records.append((timestamp, avg_magnitude, std_magnitude, se_magnitude))
        
                vis_frame = cv2.resize(frame, (gray_zoomed.shape[1], gray_zoomed.shape[0]))
                for y in range(0, flow.shape[0], block_size):
                    for x in range(0, flow.shape[1], block_size):
                        dx, dy = flow[y, x]
                        start_point = (x, y)
                        end_point = (int(x + dx), int(y + dy))
                        cv2.arrowedLine(vis_frame, start_point, end_point, color=(0, 255, 0), thickness=1, tipLength=0.3)
        
                label = f"t = {timestamp:.2f}s, speed = {avg_magnitude:.2f} pixels/frame"
                cv2.putText(vis_frame, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                gif_frames.append(cv2.cvtColor(vis_frame, cv2.COLOR_BGR2RGB))
        
                prev_gray_zoomed = gray_zoomed
                current_frame += 1
        
            cap.release()
        
            imageio.mimsave("lava_flow_vectors.gif", gif_frames, duration=1 / fps)
            
            speed_array = np.array(speed_records)
            means = speed_array[:, 1]
            stds = speed_array[:, 2]
            ses = speed_array[:, 3]
        
            var_of_means = np.var(means)
            mean_std = np.mean(stds)
            mean_se = np.mean(ses)
        
            with open("our_vid_speeds_pixels.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([])  # Empty row
                writer.writerow(["--- Summary ---"])
                writer.writerow(["Variance of the means", var_of_means])
                writer.writerow(["Mean standard deviation", mean_std])
                writer.writerow(["Mean standard error", mean_se])
        
        
            print("\n--- Summary ---")
            print(f"Variance of the means: {var_of_means:.4f}")
            print(f"Mean standard deviation: {mean_std:.4f}")
            print(f"Mean standard error: {mean_se:.4f}")
            
            times = speed_array[:, 0]
            means = speed_array[:, 1]
            stds = speed_array[:, 2]
            ses = speed_array[:, 3]
        
            plt.figure(figsize=(10, 6))
            plt.plot(times, means, label='Mean Speed', color='orange')
            plt.fill_between(times, means - stds, means + stds, color='orange', alpha=0.2, label='Std Dev')
            plt.fill_between(times, means - ses, means + ses, color='blue', alpha=0.2, label='Standard Error')
            plt.xlabel("Time (s)")
            plt.ylabel("Speed (pixels/frame)")
            plt.title("Lava Flow Speed Over Time")
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.savefig("lava_flow_speed_plot.png", dpi=300)
            plt.show()
        
        
        if __name__ == "__main__":
            main()
        # %%
        #Aljosha Video
        video_path = "/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/A2.mp4"
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        
        cv2.imwrite("first_frame.png", frame)
        print(" Frame saved as 'first_frame.png'")
        
        # Get resolution
        height, width, _ = frame.shape
        print(f"Frame resolution: {width} × {height} pixels")
        
        # %%
        
        #our video
        video_path = "/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/M1.mp4"
        cap = cv2.VideoCapture(video_path)
        frame_number = 27848  # Change this to the desired frame number
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        
        cv2.imwrite("first_frame_2.png", frame)
        print("Frame saved as 'first_frame.png")
        
        height, width, _ = frame.shape
        print(f"Frame resolution: {width} × {height} pixels")
    """,
    other="",
    code_blocks=None
)

message_1 = Message(
    conversation_id=CONVERSATION_ID,
    role="assistant",
    message_text="""
    Absolutely! If you simply want to generate a GIF of a video segment (without any block matching or motion estimation), here’s a clean and minimal snippet for that.

    ✅ Code Snippet: Generate a GIF from a Video Segment
    python
    Kopieren
    Bearbeiten
    import cv2
    import imageio
    import numpy as np

    def video_to_gif(video_path, start_sec, end_sec, frame_skip=1, resize_factor=1.0, gif_name="output.gif"):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        start_frame = int(start_sec * fps)
        end_frame = int(end_sec * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        gif_frames = []
        current_frame = start_frame

        print(f"Creating GIF from {start_sec}s to {end_sec}s ({start_frame} to {end_frame} frames)...")

        while cap.isOpened() and current_frame < end_frame:
            ret, frame = cap.read()
            if not ret:
                break

            if (current_frame - start_frame) % frame_skip != 0:
                current_frame += 1
                continue

            # Resize if needed
            if resize_factor != 1.0:
                frame = cv2.resize(frame, None, fx=resize_factor, fy=resize_factor, interpolation=cv2.INTER_AREA)

            # Convert BGR to RGB for imageio
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gif_frames.append(rgb_frame)

            current_frame += 1

        cap.release()

        # Save the GIF
        imageio.mimsave(gif_name, gif_frames, duration=1 / fps)
        print(f"GIF saved as '{gif_name}'")

    # Example usage:

    # Aljosha video
    video_to_gif(
        video_path="/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/A2.mp4",
        start_sec=5 * 60 + 4,
        end_sec=5 * 60 + 8,
        gif_name="Aljosha_scene.gif"
    )

    # Your video
    video_to_gif(
        video_path="/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/M1.mp4",
        start_sec=7 * 60 + 44,
        end_sec=7 * 60 + 48,
        gif_name="Our_scene.gif"
    )
    ⚙️ Options you can tweak:
    frame_skip=1 → set higher (e.g. 2 or 3) to make the GIF shorter/smoother

    resize_factor=0.5 → downscale to make a smaller file

    gif_name="..." → set your own filename

    Let me know if you'd like to add text overlays, bounding boxes, or timestamp labels per frame in the GIF!
    """,
    model_version=MODEL_VERSION,
    message_order=1,
    conversational="",
    code="",
    other="",
    code_blocks=[{
        'language': "python",
        'code': """
                    import cv2
    import imageio
    import numpy as np

    def video_to_gif(video_path, start_sec, end_sec, frame_skip=1, resize_factor=1.0, gif_name="output.gif"):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        start_frame = int(start_sec * fps)
        end_frame = int(end_sec * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        gif_frames = []
        current_frame = start_frame

        print(f"Creating GIF from {start_sec}s to {end_sec}s ({start_frame} to {end_frame} frames)...")

        while cap.isOpened() and current_frame < end_frame:
            ret, frame = cap.read()
            if not ret:
                break

            if (current_frame - start_frame) % frame_skip != 0:
                current_frame += 1
                continue

            # Resize if needed
            if resize_factor != 1.0:
                frame = cv2.resize(frame, None, fx=resize_factor, fy=resize_factor, interpolation=cv2.INTER_AREA)

            # Convert BGR to RGB for imageio
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gif_frames.append(rgb_frame)

            current_frame += 1

        cap.release()

        # Save the GIF
        imageio.mimsave(gif_name, gif_frames, duration=1 / fps)
        print(f"GIF saved as '{gif_name}'")

    # Example usage:

    # Aljosha video
    video_to_gif(
        video_path="/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/A2.mp4",
        start_sec=5 * 60 + 4,
        end_sec=5 * 60 + 8,
        gif_name="Aljosha_scene.gif"
    )

    # Your video
    video_to_gif(
        video_path="/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/M1.mp4",
        start_sec=7 * 60 + 44,
        end_sec=7 * 60 + 48,
        gif_name="Our_scene.gif"
    )
                """
    }]
)

message_2 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text="oder exportiere als kleine viseos?",
    model_version="",
    message_order=2,
    conversational="oder exportiere als kleine viseos?",
    code="",
    other="",
    code_blocks=None
)

message_3 = Message(
    conversation_id=CONVERSATION_ID,
    role="assistant",
    message_text="""
    ChatGPT:
    Ja klar! Du kannst ganz einfach kleine Video-Clips (z. B. MP4) aus deinen gewünschten Szenen exportieren – statt als GIF. Vorteil: kleinere Datei, bessere Qualität, mehr Kontrolle (z. B. Audio, Codec etc.).

    ✅ Code Snippet: Export Video Segment as MP4
    python
    Kopieren
    Bearbeiten
    import cv2

    def export_video_clip(video_path, start_sec, end_sec, output_path, resize_factor=1.0, frame_skip=1):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        start_frame = int(start_sec * fps)
        end_frame = int(end_sec * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        # Read one frame to get size info
        ret, frame = cap.read()
        if not ret:
            print("Could not read frame from video.")
            return

        if resize_factor != 1.0:
            frame = cv2.resize(frame, None, fx=resize_factor, fy=resize_factor, interpolation=cv2.INTER_AREA)

        height, width = frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'XVID'
        out = cv2.VideoWriter(output_path, fourcc, fps // frame_skip, (width, height))

        # Reset to start frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        current_frame = start_frame

        print(f"Exporting video from {start_sec}s to {end_sec}s → {output_path}")

        while cap.isOpened() and current_frame < end_frame:
            ret, frame = cap.read()
            if not ret:
                break

            if (current_frame - start_frame) % frame_skip == 0:
                if resize_factor != 1.0:
                    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
                out.write(frame)

            current_frame += 1

        cap.release()
        out.release()
        print("Export complete!")

    # Example usage:

    # Aljosha video
    export_video_clip(
        video_path="/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/A2.mp4",
        start_sec=5 * 60 + 4,
        end_sec=5 * 60 + 8,
        output_path="Aljosha_clip.mp4",
        resize_factor=0.5
    )

    # Your video
    export_video_clip(
        video_path="/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/M1.mp4",
        start_sec=7 * 60 + 44,
        end_sec=7 * 60 + 48,
        output_path="Our_clip.mp4",
        resize_factor=0.5
    )
    🔧 Optionen:
    resize_factor: z. B. 0.5 halbiert die Größe (gut für Präsentationen).

    frame_skip: z. B. 2 macht das Video schneller/kürzer.

    fourcc: wähle mp4v für .mp4 oder XVID für .avi

    Möchtest du auch Text oder Zeitstempel ins Video einfügen? Ich kann dir gern eine Version mit Overlays schreiben.
    """,
    model_version=MODEL_VERSION,
    message_order=3,
    conversational="",
    code="",
    other="",
    code_blocks=[{
        'language': "python",
        'code': """
                    import cv2

    def export_video_clip(video_path, start_sec, end_sec, output_path, resize_factor=1.0, frame_skip=1):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        start_frame = int(start_sec * fps)
        end_frame = int(end_sec * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        # Read one frame to get size info
        ret, frame = cap.read()
        if not ret:
            print("Could not read frame from video.")
            return

        if resize_factor != 1.0:
            frame = cv2.resize(frame, None, fx=resize_factor, fy=resize_factor, interpolation=cv2.INTER_AREA)

        height, width = frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'XVID'
        out = cv2.VideoWriter(output_path, fourcc, fps // frame_skip, (width, height))

        # Reset to start frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        current_frame = start_frame

        print(f"Exporting video from {start_sec}s to {end_sec}s → {output_path}")

        while cap.isOpened() and current_frame < end_frame:
            ret, frame = cap.read()
            if not ret:
                break

            if (current_frame - start_frame) % frame_skip == 0:
                if resize_factor != 1.0:
                    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
                out.write(frame)

            current_frame += 1

        cap.release()
        out.release()
        print("Export complete!")

    # Example usage:

    # Aljosha video
    export_video_clip(
        video_path="/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/A2.mp4",
        start_sec=5 * 60 + 4,
        end_sec=5 * 60 + 8,
        output_path="Aljosha_clip.mp4",
        resize_factor=0.5
    )

    # Your video
    export_video_clip(
        video_path="/Users/miajanzen/Documents/Master_Remote_sensing/Semester_3/SDA/M1.mp4",
        start_sec=7 * 60 + 44,
        end_sec=7 * 60 + 48,
        output_path="Our_clip.mp4",
        resize_factor=0.5
    )
                """
    }]
)

user_63_convo_19 = [message_0, message_1, message_2, message_3]
