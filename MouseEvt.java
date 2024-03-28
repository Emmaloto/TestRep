import java.awt.*;
import java.awt.event.*;
import javax.swing.*;


// This class requires the entire project to run


@SuppressWarnings("serial")
public class MouseEvt extends JFrame implements MouseListener, 
												MouseMotionListener,
												KeyListener{
  private JPanel mouseP;
  private JLabel statusBar;
  private boolean inLine;
  private SimpleGame game = new SimpleGame(this);
  

  
  public static void main(String args[]){
	  
	  new MouseEvt();
	  
  }

  public MouseEvt(){
      super("Brick Breaker");
	  
      setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);  //Close window on exit
 	  setSize(1000,1000);
	  setVisible(true);

	  add(game);
      statusBar = new JLabel("default");
      add(statusBar,  BorderLayout.SOUTH);
      
     

      addMouseListener(this);
      addMouseMotionListener(this);
      addKeyListener(this);
   }


	

  public void mouseDragged(MouseEvent e) {

	game.moveBrickTo(e.getX() , e.getY());
  }


  public void mouseMoved(MouseEvent e) {

	/*if(e.getX() == getX()){ // NOPE!
		inLine = true;	
	System.out.println("Yup  ");}
	
	game.movePaddleTo(e.getX(), e.getY());
	game.setPaddleX(e.getX());*/
	
	game.movePaddleTo(e.getX());
	
  }


  public void mouseClicked(MouseEvent e) {
	
	statusBar.setText(String.format("Click at %d, %d", e.getX(), e.getY()));
	
  }


  public void mousePressed(MouseEvent e) {
	
  }


  public void mouseReleased(MouseEvent e) {
	
  }


  public void mouseEntered(MouseEvent e) {
	statusBar.setText("You entered the area");
	//getContentPane().setBackground(Color.RED);	

  }


  public void mouseExited(MouseEvent e) {

	statusBar.setText("You left the area");
	//getContentPane().setBackground(Color.WHITE);	
	inLine = false; 	
  }

  public void keyPressed(KeyEvent e) {
    if(e.getKeyCode() == KeyEvent.VK_P){
    	System.out.printf("\n P is pressed!\n\n"); 
    	game.pause();
	    
	    
    }else if(e.getKeyCode() == KeyEvent.VK_R){
    	System.out.printf("\n R is pressed!\n\n"); 
    	game.proceed();
    	
    }
  }


  public void keyReleased(KeyEvent e) {

	
  }


  public void keyTyped(KeyEvent e) {

	
  }

}