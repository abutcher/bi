;;;; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; magic numbers

(defparameter *most*  most-positive-fixnum)
(defparameter *least* most-negative-fixnum)
(defparameter *zip* (/ 1 *most*))

;;; test engine. adapted (simplied) from http://j.mp/fWeKZL

(defparameter *tests* nil)

(defmacro deftest (name params  &body body)
  "Create a defun, adding it name to the list of *tests*."
  `(progn (unless (member ',name *tests*) (push ',name *tests*))
      (defun ,name ,params ,@body)))

(let ((pass 0)  
      (fail 0)) 
  (defun test (want got)
    "Run one test, comparing 'want' to 'got'."
    (labels  
	((white (c) ; returns nil if 'c' is not white space
	   (member c '(#\# #\\ #\Space #\Tab #\Newline
		       #\Linefeed #\Return #\Page) :test #'char=))
	 (whiteout (s)  ; remove all white space
	   (remove-if #'white s)) 
	 (samep (x y) ; true if strings of x&y, sans whitespace, are the same
	   (string= (whiteout (format nil "~(~a~)" x)) 
		    (whiteout (format nil "~(~a~)" y)))))
      (cond ((samep want got) (incf pass))
	    (t                (incf fail)
			      (format t "~&; fail : expected ~a~%" want)))
      got))

  (defun tests ()
    "Run all the tests in *tests*."
    (labels ((run (x) (format t "~&;testing  ~a~%" x) (funcall x)))
      (when *tests*
	(setf fail 0 pass 0)
	(mapcar #'run (reverse *tests*))
	(format t "~&; pass : ~a = ~5,1f% ~%; fail : ~a = ~5,1f% ~%"
		pass (* 100 (/ pass (+ pass fail)))
		fail (* 100 (/ fail (+ pass fail)))))))
  )

(deftest !deftest1 (&aux (a 1)) 
  "testing test"
  (test (+ a 1) 2)) 

(deftest !deftest2 (&aux (a 1)) 
  "testing test: this time, with a failure."
  (test (+ a 1) 3)) 

(deftest !deftest3 ()
  "testing tests defined using some other complicated function."
  (test (my-complicated-thing)
    '(3 4 5)))

(defun my-complicated-thing ()
  (member 3 '(1 2 3 4 5)))

;;; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; macros
(defmacro oo (&rest l)
  "Print a symbol and its binding."
  `(progn (terpri) (o ,@l)))

(defmacro o (&rest l)
  "Print a list of symbols and their bindings."
  (let ((last (gensym)))
    `(let (,last)
       ,@(mapcar #'(lambda(x) `(setf ,last (oprim ,x))) l)
       (terpri)
       ,last)))

(defmacro oprim (x)
  "Print a thing and its binding, then return thing."
  `(progn (format t "~&[~a]=[~a] " (quote ,x) ,x) ,x))

(defmacro doitems ((one n list &optional out) &body body )
  "Set 'one' and 'n' to each item in a list, and its position."
  `(let ((,n -1))
     (dolist (,one ,list ,out)
       (incf ,n)
       ,@body)))

(defmacro do12 ((one two list &optional out) &body body)
  "Set 'one' and 'two' to each par of adjecent items in a list."
  `(let ((,one (car ,list)))
     (dolist (,two (cdr ,list) ,out)
       ,@body
       (setf ,one ,two))))

(defmacro dohash ((key value hash &optional end) &body body)
  "Iterate through all keys and values in a hash."
  `(progn (maphash #'(lambda (,key ,value)
		       ,@body)
		   ,hash)
	  ,end))

(defmacro dovalues ((value hash &optional end) &body body)
  "Iterate through all values in a hash."
  (let ((key (gensym)))
    `(progn (maphash #'(lambda (,key ,value)
			 (declare (ignore ,key))
			 ,@body)
		     ,hash)
	    ,end)))

;;; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; vectors

(defmacro dovs ((one n vector &optional out) &body body )
  "Set 'one' and 'n' to each item in a vector, and its position."
  `(dotimes (,n (length ,vector) ,out)
     (let ((,one (svref ,vector ,n)))
       ,@body)))

(defmacro dov ((one vector &optional out) &body body)
  (let ((n (gensym)))
    `(dotimes (,n (length ,vector) ,out)
       (let ((,one (svref ,vector ,n)))
	 ,@body))))
 
(defun anyv (v)
  (svref v (randi (length v))))

(defun vector! (l)
  (coerce l 'vector))

(defun lastv (v)
  (svref v (1- (length v))))

(defun shufflev (v)
  "shuffle order of items in a vector"
  (dotimes (i (length v) v)
    (rotatef
     (svref  v i)
     (svref  v (randi (length v))))))

;;; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; random number generation

(let* ((seed0      10013)
       (seed       seed0)
       (multiplier 16807.0d0)
       (modulus    2147483647.0d0))
  (defun reset-seed ()  (setf seed seed0))
  (defun randf      (n) (* n (- 1.0d0 (park-miller-randomizer))))
  (defun randi      (n) (floor (* n (/ (randf 1000.0) 1000))))
  (defun park-miller-randomizer ()
    "cycle= 2,147,483,646 numbers"
    (setf seed (mod (* multiplier seed) modulus))
    (/ seed modulus))
)

(deftest !rands ()
  (reset-seed)
  (dotimes (i 11) (randf 100))
  (test (randf 100) 8.386648357094572d0)
  (reset-seed)
  (test (randf 100) 92.16345646053713d0))

;;; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; misc lib

;Easy definition of anonymous small functions. 
;Arguments are '_', '_1', ..., '_5'." 
;Contenious: see http://j.mp/heV6yn
(defmacro _ (&body body) 
  `(lambda (&optional _1 _2 _3 _4 _5) 
     (declare (ignorable _1 _2 _3 _4 _5)) 
     (let ((_ _1)) 
       (declare (ignorable _)) 
       ,@body))) 

(defmethod print-object ((h hash-table) str)
  "Change the print method for a hash."
  (format str "{hash of ~a items}" (hash-table-count h)))

(defun shuffle (l)
  "shuffle order of items in a list"
  (dotimes (i (length l) l)
    (rotatef
     (elt l i)
     (elt l (randi (length l))))))

(defun visit (fn l)
  "apply fn to all items in nested lists"
  (if (atom l)
      (funcall fn l)
      (dolist (one l)
	(visit fn one))))

(defun issamp (task wme &optional (n 20))
  "N times, try to perform some problem."
  (unless (< n 1)
    (or (catch :restart
	  (funcall task (funcall wme)))
	(issamp task wme (1- n)))))

(defun nchars (&optional (n 40) (c #\Space))
  (with-output-to-string (s)
    (dotimes (i n)
      (format s "~a" c))))

(defun read1 (f)
  (with-open-file (str f) 
    (read str nil)))

(defun positions (l p)
  (let (out)
    (doitems (one n l out)
	     (if (funcall p one)
		 (push n out)))))

(defun sort-syms (l)
  (sort l
	(lambda (x y) (string< (symbol-name x) (symbol-name y)))))

;;; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; list tricks

(defun select (selector-fn facts)
  "return all list items satisying selector-fn"
  (remove-if-not selector-fn facts))

(defun flatten (l)
  (let (out)
    (visit #'(lambda (one) (push one out)) l)
    (reverse out)))


;;; ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; profiling tricks

(defmacro time-it (n &body body) 
  "Run 'body' 'n' times."
  (let ((n1 (gensym)) 
        (i  (gensym))
        (t1 (gensym)))
    `(let ((,n1 ,n)
           (,t1 (get-internal-run-time)))
       (dotimes (,i ,n1) ,@body)
       (float (/ (- (get-internal-run-time) ,t1)
                 (* ,n1 internal-time-units-per-second))))))

(deftest !time-it (&key (repeats 100) (loops 100) (max 10))
  "Add up 'loops' random numbers."
  (reset-seed)
  (let (out) 
    (dotimes (i loops) 
      (push (randf max) out)) 
    (time-it repeats
      (apply #'+ out))))

(defmacro watch (code)
  "Run the code, print number of calls for functions used in code."
  `(progn
    (sb-profile:unprofile)
    (sb-profile:reset)
    (sb-profile:profile ,@(my-funs))
    (eval (prog1 t ,code))
    (sb-profile:report)
    (sb-profile:unprofile)
    t)
)

(defun my-funs ()
  "Return a list of functions that are not in core LISP."
  (let ((out '()))
    (do-symbols  (s)
      (if (and (fboundp s)
	       (find-symbol  (format nil "~a" s) *package*)
	       (not (member s (lispfuns))))
	  (push s out)))
    out))

  (defun lispfuns ()
    '(* * ** *** + + ++ +++ - - / / // /// 1+ 1- < <= = > >= abort abs
      acons acos acosh add-method adjoin adjust-array adjustable-array-p
      alpha-char-p alphanumericp alter always and append append appending
      apply applyhook *applyhook* apropos apropos-list aref arithmetic-error
      arithmetic-error-operands arithmetic-error-operation array-dimension
      array-dimension-limit array-dimensions array-element-type
      array-has-fill-pointer-p array-in-bounds-p array-rank array-rank-limit
      array-row-major-index array-total-size array-total-size-limit arrayp
      as ash asin asinh assert assert assoc assoc-if assoc-if-not atan
      atanh atom augment-environment bit bit-and bit-andc1 bit-andc2
      bit-eqv bit-ior bit-nand bit-nor bit-not bit-orc1 bit-orc2 bit-vector-p
      bit-xor block boole both-case-p boundp break break *break-on-signals*
      *break-on-warnings* broadcast-stream-streams butlast byte byte-position
      byte-size caaaar caaadr caaar caadar caaddr caadr caar cadaar cadadr
      cadar caddar cadddr caddr cadr call-arguments-limit call-method
      call-next-method car case catch catenate ccase ccase cdaaar cdaadr
      cdaar cdadar cdaddr cdadr cdar cddaar cddadr cddar cdddar cddddr
      cdddr cddr cdr ceiling cell-error cell-error-name cerror cerror
      change-class char char-bit char-bits char-bits-limit char-code
      char-code-limit char-control-bit char-downcase char-equal char-font
      char-font-limit char-greaterp char-hyper-bit char-int char-lessp
      char-meta-bit char-name char-not-equal char-not-greaterp char-not-lessp
      char-super-bit char-upcase char/= char< char<= char= char> char>=
      character characterp check-type check-type choose choose-if chunk
      cis class-name class-of clear-input close clrhash code-char coerce
      collect collect collect-alist collect-and collect-append collect-file
      collect-first collect-fn collect-hash collect-last collect-length
      collect-max collect-min collect-nconc collect-nth collect-or
      collect-plist collect-sum collecting collecting-fn commonp compile
      compile-file compile-file-pathname *compile-file-pathname*
      *compile-file-truename* *compile-print* *compile-verbose*
      compiled-function-p compiler-let compiler-let compiler-macro-function
      compiler-macroexpand compiler-macroexpand-1 complement complex
      complexp compute-applicable-methods compute-restarts concatenate
      concatenated-stream-streams cond condition conjugate cons consp
      constantp continue control-error copy-alist copy-list copy-pprint-dispatch
      copy-readtable copy-seq copy-symbol copy-tree cos cosh cotruncate
      count count count-if count-if-not counting ctypecase ctypecase
      *debug-io* *debugger-hook* decf declaim declaration-information
      declare decode-float decode-universal-time *default-pathname-defaults*
      defclass defgeneric define-compiler-macro define-condition
      define-declaration define-method-combination define-modify-macro
      define-setf-method defmacro defmethod defpackage defstruct deftype
      defun defvar delete delete-duplicates delete-file delete-if
      delete-if-not delete-package denominator deposit-field describe
      describe-object destructuring-bind digit-char digit-char-p directory
      directory-namestring disassemble division-by-zero do do do*
      do-all-symbols do-external-symbols do-symbols documentation
      documentation doing dolist dotimes double-float-epsilon
      double-float-negative-epsilon dpb dribble ecase echo-stream-input-stream
      echo-stream-output-stream ed eighth elt encapsulated enclose
      encode-universal-time end-of-file endp enough-namestring
      ensure-generic-function eq eql equal equalp error error error
      *error-output* etypecase etypecase eval eval-when evalhook *evalhook*
      evenp every exp expand export expt fboundp fdefinition *features*
      ffloor fifth file-author file-error file-error-pathname file-length
      file-namestring file-position file-string-length file-write-date
      fill fill-pointer finally find find-all-symbols find-class find-if
      find-if-not find-method find-package find-restart find-symbol
      finish-output first flet float float-digits float-precision float-radix
      float-sign floating-point-overflow floating-point-underflow floatp
      floor for format formatter fourth funcall function function-information
      function-keywords function-lambda-expression functionp gatherer
      gathering gcd generator generic-flet generic-function generic-labels
      gensym *gensym-counter* gentemp get get-decoded-time get-internal-real-time
      get-internal-run-time get-output-stream-string get-properties
      get-setf-method get-setf-method-multiple-value get-universal-time
      getf gethash go graphic-char-p handler-bind handler-case hash-table-count
      hash-table-p hash-table-rehash-size hash-table-rehash-threshold
      hash-table-size hash-table-test host-namestring identity if if
      ignore-errors imagpart import in-package in-package incf
      initialize-instance initially input-stream-p inspect int-char
      integer-decode-float integer-length integerp interactive-stream-p
      intern internal-time-units-per-second intersection invalid-method-error
      invoke-debugger invoke-restart isqrt iterate keywordp lambda-list-keywords
      lambda-parameters-limit last latch lcm ldb ldb-test ldiff
      least-negative-double-float least-negative-long-float
      least-negative-normalized-double-float least-negative-normalized-long-float
      least-negative-normalized-short-float
      least-negative-normalized-single-float least-negative-short-float
      least-negative-single-float least-positive-double-float
      least-positive-long-float least-positive-normalized-double-float
      least-positive-normalized-long-float least-positive-normalized-short-float
      least-positive-normalized-single-float least-positive-short-float
      least-positive-single-float length let let* lisp-implementation-type
      lisp-implementation-version list list* list-all-packages list-length
      listen listp load load-logical-pathname-translations *load-pathname*
      *load-print* load-time-value *load-truename* *load-verbose* locally
      locally log logand logandc1 logandc2 logbitp logcount logeqv
      logical-pathname logical-pathname logical-pathname-translations
      logior lognand lognor lognot logorc1 logorc2 logtest logxor
      long-float-epsilon long-float-negative-epsilon long-site-name loop
      loop-finish lower-case-p machine-instance machine-type machine-version
      macro-function macroexpand macroexpand-1 *macroexpand-hook* make-array
      make-broadcast-stream make-char make-concatenated-stream make-condition
      make-dispatch-macro-character make-echo-stream make-hash-table
      make-instance make-instances-obsolete make-list make-load-form
      make-load-form-saving-slots make-package make-pathname make-random-state
      make-sequence make-string make-string-input-stream
      make-string-output-stream make-symbol make-synonym-stream
      make-two-way-stream makunbound map map-fn map-into mapc mapcan
      mapcar mapcon maphash mapl maplist mapping mask mask-field max
      maximize maximizing member member-if member-if-not merge merge-pathnames
      method-combination-error method-qualifiers min mingle minimize
      minimizing minusp mismatch mod *modules* most-negative-double-float
      most-negative-fixnum most-negative-long-float most-negative-short-float
      most-negative-single-float most-positive-double-float most-positive-fixnum
      most-positive-long-float most-positive-short-float
      most-positive-single-float muffle-warning multiple-value-bind
      multiple-value-call multiple-value-list multiple-value-prog1
      multiple-value-setq multiple-values-limit name-char named namestring
      nbutlast nconc nconc nconcing never next-in next-method-p next-out
      nil nintersection ninth no-applicable-method no-next-method not
      notany notevery nreconc nreverse nset-difference nset-exclusive-or
      nstring-capitalize nstring-downcase nstring-upcase nsublis nsubst
      nsubst-if nsubst-if-not nsubstitute nsubstitute-if nsubstitute-if-not
      nth nth-value nthcdr null numberp numerator nunion oddp off-line-port
      open open-stream-p optimizable-series-function or output-stream-p
      *package* package-error package-error-package package-name
      package-nicknames package-shadowing-symbols package-use-list
      package-used-by-list packagep pairlis parse-integer parse-macro
      parse-namestring pathname pathname-device pathname-directory
      pathname-host pathname-match-p pathname-name pathname-type
      pathname-version pathnamep peek-char phase pi plusp pop position
      position-if position-if-not positions pprint-dispatch
      pprint-exit-if-list-exhausted pprint-fill pprint-indent pprint-linear
      pprint-logical-block pprint-newline pprint-pop pprint-tab pprint-tabular
      previous prin1 *print-array* *print-base* *print-case* *print-circle*
      *print-escape* *print-gensym* *print-length* *print-level* *print-lines*
      *print-miser-width* print-object *print-pprint-dispatch* *print-pretty*
      *print-radix* *print-readably* *print-right-margin* print-unreadable-object
      probe-file proclaim producing prog prog* prog1 prog2 progn program-error
      progv propagate-alterability provide psetf psetq push pushnew
      *query-io* quote random *random-state* random-state-p rassoc rassoc-if
      rassoc-if-not rational rationalize rationalp read *read-base*
      read-byte read-char read-char-no-hang *read-default-float-format*
      read-delimited-list *read-eval* read-from-string read-line
      read-preserving-whitespace *read-suppress* *readtable* readtable-case
      readtablep realp realpart reduce reinitialize-instance rem remf
      remhash remove remove-duplicates remove-method remprop rename-file
      rename-package repeat replace require rest restart restart-bind
      restart-case restart-name result-of return return return-from
      revappend reverse room rotatef round row-major-aref rplaca rplacd
      sbit scale-float scan scan-alist scan-file scan-fn scan-fn-inclusive
      scan-hash scan-lists-of-lists scan-lists-of-lists-fringe scan-multiple
      scan-plist scan-range scan-sublists scan-symbols schar search second
      series series series-element-type serious-condition set set-char-bit
      set-difference set-dispatch-macro-character set-exclusive-or
      set-macro-character set-pprint-dispatch set-syntax-from-char setf
      setq seventh shadow shadowing-import shared-initialize shiftf
      short-float-epsilon short-float-negative-epsilon short-site-name
      signal signum simple-bit-vector-p simple-condition
      simple-condition-format-arguments simple-condition-format-string
      simple-error simple-string-p simple-type-error simple-vector-p
      simple-warning sin single-float-epsilon single-float-negative-epsilon
      sinh sixth sleep slot-boundp slot-exists-p slot-makunbound slot-missing
      slot-unbound slot-value software-type software-version some sort
      special-form-p split split-if sqrt stable-sort standard-char-p
      *standard-input* *standard-output* step storage-condition store-value
      stream-element-type stream-error stream-error-stream stream-external-format
      streamp string string-capitalize string-char-p string-downcase
      string-equal string-greaterp string-left-trim string-lessp
      string-not-equal string-not-greaterp string-not-lessp string-right-trim
      string-trim string-upcase string/= string< string<= string= string>
      string>= stringp sublis subseq subseries subsetp subst subst-if
      subst-if-not substitute substitute-if substitute-if-not subtypep
      sum summing *suppress-series-warnings* svref sxhash symbol-function
      symbol-macrolet symbol-name symbol-package symbol-plist symbol-value
      symbolp synonym-stream-symbol t tagbody tailp tan tanh tenth
      *terminal-io* terminate-producing terpri the thereis third throw
      time to-alter trace *trace-output* translate-logical-pathname
      translate-pathname tree-equal truename truncate two-way-stream-input-stream
      two-way-stream-output-stream type-error type-error-datum
      type-error-expected-type type-of typecase typep unbound-variable
      undefined-function unexport unintern union unless unless unread-char
      until until-if untrace unuse-package unwind-protect
      update-instance-for-different-class update-instance-for-redefined-class
      upgraded-array-element-type upgraded-complex-part-type upper-case-p
      use-package use-value user-homedir-pathname values values-list
      variable-information vector vector-pop vector-push vector-push-extend
      warn warning when when while wild-pathname-p with with-accessors
      with-added-methods with-compilation-unit with-condition-restarts
      with-hash-table-iterator with-input-from-string with-open-file
      with-open-stream with-output-to-string with-package-iterator
      with-simple-restart with-slots with-standard-io-syntax write
      write-byte write-char write-string write-to-string y-or-n-p yes-or-no-p
      zerop unprofile reset report profile stream-read-char-no-hang
      stream-fresh-line stream-peek-char stream-write-char stream-write-byte
      stream-write-string stream-line-column stream-write-sequence
      stream-read-byte stream-read-line stream-line-length stream-read-sequence
      stream-read-char stream-clear-output stream-unread-char stream-clear-input
      stream-finish-output stream-start-line-p stream-force-output
      stream-terpri stream-advance-to-column stream-file-position
      stream-listen weak-pointer-p package-locked-p step-condition-result
      native-pathname defconstant-uneql-new-value defconstant-uneql-name
      cancel-finalization purify process-status-hook process-output
      timer-scheduled-p package-lock-violation process-plist interactive-eval
      list-all-timers process-p process-status get-bytes-consed process-error
      defconstant-uneql-old-value hash-table-weakness step-next
      package-implements-list float-nan-p octets-to-string with-unlocked-packages
      enable-debugger float-denormalized-p with-timeout
      package-locked-error-symbol process-pid package-implemented-by-list
      process-pty posix-getenv step-condition-args gc-off finalize
      without-package-locks unschedule-timer schedule-timer make-timer
      native-namestring parse-native-namestring float-infinity-p lock-package
      process-kill process-exit-code step-continue string-to-octets
      unlock-package quit process-alive-p remove-implementation-package
      find-executable-in-search-path weak-pointer-value process-wait
      disable-debugger process-core-dumped define-source-context
      add-implementation-package run-program process-close step-condition-form
      posix-environ timer-name process-input bytes-consed-between-gcs
      gc-on make-weak-pointer save-lisp-and-die describe-compiler-policy
      step-into gc float-trapping-nan-p truly-the internal-debug
      frame-has-debug-tag-p backtrace-as-list arg var backtrace
      unwind-to-frame-and-call slot alien-funcall def-alien-variable deref
      addr with-alien load-shared-object define-alien-routine def-alien-routine
      make-alien free-alien alien-sap cast get-errno load-foreign sap-alien
      def-alien-type null-alien define-alien-type define-alien-variable
      extern-alien load-1-foreign alien-size clear-output print princ-to-string
      defsetf remove-if-not vectorp print-not-readable-object copy-structure
      read-sequence get-dispatch-macro-character define-setf-expander
      fmakunbound write-sequence constantly labels prin1-to-string
      get-setf-expansion defconstant simple-condition-format-control
      ensure-directories-exist unbound-slot-instance /= get-macro-character
      allocate-instance remove-if array-displacement fceiling special-operator-p
      force-output princ lambda invoke-restart-interactively ftruncate
      fround write-line macrolet define-symbol-macro pprint fresh-line
      defparameter))
