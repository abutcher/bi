(defstruct range
  (max *least*)
  (min *most*)
  )



(defun range-update (n r)
  (when r
    (unless (unknownp n)
      (setf (range-max  r) (max n (range-max r))
	    (range-min  r) (min n (range-min r))))))

(defun range0 (x) 
  (if (nump x)
      (make-range)))

(defun norm (n  r)
  (cond ((unknownp n) n)
	(r  (float (/ (- n             (range-min r))
		      (- (range-max r) (range-min r)))))
	(t n)))
