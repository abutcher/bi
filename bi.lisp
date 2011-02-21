(defun make (&rest files)
   (handler-bind
      ((style-warning #'muffle-warning))
   (dolist (f files)
(load f))))

(defun make-bi ()
  (make "lisp/tricks"
	"lisp/range"
	"lisp/table"
))

(defun make-effort ()
  (make "lisp/data/albrecht"
	"lisp/data/china"
	"lisp/data/nasa93"
))

(make-bi)
;(make-effort)