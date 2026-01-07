use crate::models::Progress;

/// Parse duration from FFprobe output
pub fn parse_duration(output: &str) -> f64 {
    let re = regex::Regex::new(r"Duration: (\d+):(\d+):(\d+\.?\d*)").unwrap();
    if let Some(caps) = re.captures(output) {
        let hours: f64 = caps.get(1).unwrap().as_str().parse().unwrap_or(0.0);
        let mins: f64 = caps.get(2).unwrap().as_str().parse().unwrap_or(0.0);
        let secs: f64 = caps.get(3).unwrap().as_str().parse().unwrap_or(0.0);
        return hours * 3600.0 + mins * 60.0 + secs;
    }
    0.0
}

/// Parse progress from FFmpeg stderr output
pub fn parse_progress(line: &str, duration: f64) -> Option<Progress> {
    let time_re = regex::Regex::new(r"time=(\d+):(\d+):(\d+\.?\d*)").unwrap();
    let speed_re = regex::Regex::new(r"speed=\s*([\d.]+x)").unwrap();
    let size_re = regex::Regex::new(r"size=\s*(\S+)").unwrap();

    if let Some(caps) = time_re.captures(line) {
        let hours: f64 = caps.get(1).unwrap().as_str().parse().unwrap_or(0.0);
        let mins: f64 = caps.get(2).unwrap().as_str().parse().unwrap_or(0.0);
        let secs: f64 = caps.get(3).unwrap().as_str().parse().unwrap_or(0.0);
        let current_time = hours * 3600.0 + mins * 60.0 + secs;

        let percent = if duration > 0.0 {
            (current_time / duration * 100.0).min(100.0)
        } else {
            0.0
        };

        let speed = speed_re
            .captures(line)
            .map(|c| c.get(1).unwrap().as_str().to_string())
            .unwrap_or_else(|| "N/A".to_string());

        let size = size_re
            .captures(line)
            .map(|c| c.get(1).unwrap().as_str().to_string())
            .unwrap_or_else(|| "0kB".to_string());

        return Some(Progress {
            percent,
            time: current_time,
            speed,
            size,
        });
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_duration() {
        let output = "Duration: 00:01:30.50, start: 0.000000, bitrate: 128 kb/s";
        let duration = parse_duration(output);
        assert!((duration - 90.5).abs() < f64::EPSILON);

        let output_invalid = "No duration line here";
        assert_eq!(parse_duration(output_invalid), 0.0);
    }

    #[test]
    fn test_parse_progress() {
        let line = "frame= 100 fps= 25 q=28.0 size= 1024kB time=00:00:10.00 bitrate= 838.9kbits/s speed=1.5x";
        let duration = 20.0;
        let progress = parse_progress(line, duration).unwrap();
        
        assert!((progress.percent - 50.0).abs() < f64::EPSILON);
        assert!((progress.time - 10.0).abs() < f64::EPSILON);
        assert_eq!(progress.speed, "1.5x");
        assert_eq!(progress.size, "1024kB");

        let line_invalid = "Some random buffer output";
        assert!(parse_progress(line_invalid, duration).is_none());
    }
}
