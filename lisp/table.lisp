(deftest !data ()
  (test 24 (length (table-rows (data "lisp/data/albrecht.lisp")))))

(deftest !cluster ()
  (test 24 (length (relation-rows (cluster "lisp/data/albrecht.lisp")))))

(defstruct relation
  header rows    ; data stuff
  nums syms num-klasses sym-klasses ignores sym-klass-names; column subsets
  ranges   ;  column meta-info
  )

(defstruct (table(:include relation)))

(defstruct (cluster(:include relation))
  west east xsplit ysplit quad1 quad2 quad3 quad4)

(defstruct row id raw-cells cells 2d-cells)

(defmacro thingp (x y) `(and (symbolp ,x) (find ,y (symbol-name ,x))))
(defun symp0     (x) (not (nump0 x)))
(defun nump0     (x) (thingp x #\$))
(defun goalp     (x) (thingp x #\!))
(defun ignorep   (x) (thingp x #\~))
(defun unknownp  (x) (equal x '?))

(defun num-goalp (x) (and (goalp x) (nump0 x)))
(defun sym-goalp (x) (and (goalp x) (symp0 x)))
(defun symp      (x) (and (not (goalp x)) (not (ignorep x)) (symp0 x)))
(defun nump      (x) (and (not (goalp x)) (not (ignorep x)) (nump0 x)))

(defun data (file)
  (deftable (read1 file)))

(defun cluster (file)
  (defcluster (read1 file)))
    
(defun deftable (lists)
  (let* ((id      0)
	 (data    (cdr lists))
	 (head    (car lists))
	 (ranges  (mapcar #'range0 head))
	 (tbl  (make-table 
		:header      head
		:nums        (positions head #'nump)
		:syms        (positions head #'symp)
		:ignores     (positions head #'ignorep)
		:num-klasses (positions head #'num-goalp)
		:sym-klasses (positions head #'sym-goalp)
		:ranges      ranges)))
    (labels ((min-max (row) (mapc #'range-update row ranges))
	     (row0    (raw) (make-row
			     :raw-cells  (vector! raw)
	       
			     :cells      (vector! (mapcar #'norm raw ranges))
			     :id         (incf id))))
      (mapc #'min-max data)
      (setf (table-rows tbl)
	    (vector! (mapcar #'row0 data)))
      (dov (row (table-rows tbl))
	(pushnew (sym-klass1 row tbl)
		 (table-sym-klass-names tbl)))
      tbl)))

(defun defcluster (lists)
  (let* ((id      0)
         (data    (cdr lists))
         (head    (car lists))
         (ranges  (mapcar #'range0 head))
	 (quads   (make-quads data))
	 (ticks (middle-ticks data))
	 (poles (multiple-value-list (find-poles (vector! data))))
         (tbl  (make-cluster
                :header      head
                :nums        (positions head #'nump)
                :syms        (positions head #'symp)
                :ignores     (positions head #'ignorep)
                :num-klasses (positions head #'num-goalp)
                :sym-klasses (positions head #'sym-goalp)
                :ranges      ranges
		:quad1 (construct-cluster head (first quads))
		:quad2 (construct-cluster head (second quads))
		:quad3 (construct-cluster head (third quads))
		:quad4 (construct-cluster head (fourth quads))
		:xsplit (first ticks)
		:ysplit (second ticks)
		:west (nth 0 poles)
		:east (nth 1 poles))))
    (labels ((min-max (row) (mapc #'range-update row ranges))
             (row0    (raw) (let ((coords (multiple-value-list (xy raw
					      (cluster-west tbl)
					      (cluster-east tbl)))))
			      (make-row
			       :raw-cells  (vector! raw)
			       :2d-cells   (vector! coords)
			       :cells      (vector! (mapcar #'norm raw ranges))
			       :id         (incf id)))))
      (mapc #'min-max data)
      (setf (cluster-rows tbl)
            (vector! (mapcar #'row0 data)))
      (dov (row (cluster-rows tbl))
        (pushnew (sym-klass1 row tbl)
                 (cluster-sym-klass-names tbl)))
      tbl)))

(defun construct-cluster(head list)
  (if (> 4 (length list))
      nil
      (defcluster (push head list))))
      

(defun sym-klass1 (row tbl) (car (sym-klasses row tbl)))

(defun sym-klasses (row tbl)
  (mapcar #'(lambda (i) (svref (row-cells row) i))
	  (relation-sym-klasses tbl)))
  
(defmacro do-some ((one row nums  &optional out) &body body)
  (let ((num  (gensym)))
    `(dolist (,num ,nums ,out)
       (let ((,one (svref (row-cells ,row) ,num)))
	 (unless (unknownp ,one)
	   ,@body)))))

(defmacro do-some2 ((one two row1 row2 nums  &optional out) &body body)
  (let ((num  (gensym)))
    `(dolist (,num ,nums ,out)
       (let ((,one (svref (row-cells ,row1) ,num))
	     (,two (svref (row-cells ,row2) ,num)))
	 (unless (or (unknownp ,one) (unknownp ,two))
	   ,@body)))))